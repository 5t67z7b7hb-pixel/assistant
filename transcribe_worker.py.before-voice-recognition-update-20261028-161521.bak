"""Keep one multilingual Whisper model warm in a separate, crash-isolated worker."""
import json
import configparser
import os
import sys
import time

import numpy as np
import av


# faster-whisper 1.2.x still passes this option, which PyAV 19 removed.
_av_open = av.open


def _compatible_av_open(*args, **kwargs):
    kwargs.pop("metadata_errors", None)
    return _av_open(*args, **kwargs)


av.open = _compatible_av_open

from faster_whisper import WhisperModel
from technical_glossary import (
    WHISPER_HOTWORDS,
    correct_high_confidence_terms,
    rank_glossary_terms,
)


def _configured_whisper_settings():
    """Read the ASR model/device choice from the app's config file."""
    parser = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.ini")
    parser.read(config_path, encoding="utf-8")
    model_name = parser.get("whisper", "model", fallback="small").strip() or "small"
    device = parser.get("whisper", "device", fallback="cpu").strip().lower() or "cpu"
    if device not in {"auto", "cpu", "cuda"}:
        device = "cpu"
    return model_name, device


def load_model(model_name=None, device_preference=None):
    """Load the configured multilingual model without competing with Ollama's GPU."""
    configured_model, configured_device = _configured_whisper_settings()
    model_name = model_name or configured_model
    device_preference = (device_preference or configured_device).lower()
    model = None
    if device_preference in {"auto", "cuda"}:
        try:
            import ctranslate2
            if ctranslate2.get_cuda_device_count() > 0:
                model = WhisperModel(model_name, device="cuda", compute_type="int8_float16", cpu_threads=4)
                # Model construction alone does not load CUDA kernels. Run a short
                # decode now so a broken CUDA runtime is caught before a real call.
                warmup_segments, _ = model.transcribe(
                    np.zeros(16000, dtype=np.float32), language="en", beam_size=1,
                    best_of=1, temperature=0.0, vad_filter=False,
                )
                list(warmup_segments)
                return model, f"NVIDIA GPU ({model_name})"
        except Exception as error:
            model = None
            print(json.dumps({"event": "gpu_fallback", "message": str(error)}), flush=True)
    if model is None:
        cpu_threads = max(4, min(8, os.cpu_count() or 4))
        model = WhisperModel(model_name, device="cpu", compute_type="int8", cpu_threads=cpu_threads)
        backend = f"CPU ({model_name})"
    else:
        backend = f"NVIDIA GPU ({model_name})"
    # Do the first decoder setup before the user records a question so it does
    # not land on the first answer request.
    warmup_segments, _ = model.transcribe(
        np.zeros(16000, dtype=np.float32), language="en", beam_size=1,
        best_of=1, temperature=0.0, vad_filter=False,
    )
    list(warmup_segments)
    return model, backend


def transcribe(model, audio_path, initial_prompt=None):
    started = time.perf_counter()
    segments, _ = model.transcribe(
        audio_path,
        beam_size=3,
        best_of=1,
        without_timestamps=True,
        condition_on_previous_text=False,
        initial_prompt=initial_prompt,
        language=None,
        multilingual=True,
        vad_filter=True,
        hotwords=WHISPER_HOTWORDS,
    )
    text = " ".join(segment.text for segment in segments).strip()
    text = correct_high_confidence_terms(text)
    matches = rank_glossary_terms(text)
    return {
        "text": text,
        "seconds": round(time.perf_counter() - started, 2),
        "matched_terms": matches,
    }


def serve():
    print(json.dumps({"event": "loading"}), flush=True)
    try:
        model, backend = load_model()
    except Exception as error:
        print(json.dumps({"event": "startup_error", "error": str(error)}), flush=True)
        return 1
    print(json.dumps({"event": "ready", "backend": backend}), flush=True)

    for line in sys.stdin:
        try:
            request = json.loads(line)
            if request.get("command") == "close":
                break
            result = transcribe(model, request["audio_path"], request.get("initial_prompt"))
            result["event"] = "result"
            result["backend"] = backend
            print(json.dumps(result, ensure_ascii=False), flush=True)
        except Exception as error:
            print(json.dumps({"event": "request_error", "error": str(error)}, ensure_ascii=False), flush=True)
    return 0


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--serve":
        raise SystemExit(serve())
    if len(sys.argv) < 2:
        raise SystemExit("Expected --serve or a WAV file path")
    audio_path = sys.argv[1]
    initial_prompt = sys.argv[2] if len(sys.argv) > 2 else None
    model, _ = load_model()
    print(json.dumps(transcribe(model, audio_path, initial_prompt), ensure_ascii=False))


if __name__ == "__main__":
    main()
