"""Capture microphones and Windows playback with WASAPI through SoundCard."""
import json
import os
import sys
import threading
import time
import traceback
import wave

import numpy as np
import soundcard as sc
from scipy.signal import resample_poly

TARGET_RATE = 16000
CAPTURE_RATE = 48000
BLOCK_FRAMES = 2048
MAX_SECONDS = 180
MIN_SIGNAL_RMS = 0.00005
TARGET_TRACK_RMS = 0.035
LEVEL_FRAME_SAMPLES = TARGET_RATE // 10
PREFERRED_TRACK_MIN_RATIO = 0.5


def _record_source(microphone, stop_event, chunks, state, errors):
    try:
        # Stereo capture avoids SoundCard's known mono WASAPI path issue; mono
        # devices are safely downmixed after capture.
        channel_map = [0, 1]
        with microphone.recorder(CAPTURE_RATE, channels=channel_map, blocksize=BLOCK_FRAMES) as recorder:
            while not stop_event.is_set():
                block = recorder.record(numframes=BLOCK_FRAMES)
                if not state["ready"]:
                    state["ready"] = True
                # Keep a capture-time estimate so independently opened devices
                # can be aligned before mixing their tracks.
                block_start = time.monotonic() - len(block) / CAPTURE_RATE
                chunks.append((block_start, block))
                level = float(np.sqrt(np.mean(np.asarray(block, dtype=np.float32) ** 2)))
                state["level"] = 0.65 * state["level"] + 0.35 * level
    except Exception as error:
        message = f"{microphone.name}: {error}"
        errors.append(message)
        state["error"] = str(error)


def _mono_16k(chunks):
    start_time = chunks[0][0]
    samples = np.concatenate([chunk for _, chunk in chunks], axis=0).astype(np.float32, copy=False)
    if samples.ndim > 1:
        samples = samples.mean(axis=1)
    if samples.size:
        samples = resample_poly(samples, TARGET_RATE, CAPTURE_RATE).astype(np.float32, copy=False)
    return samples, start_time


def _active_rms(samples):
    """Measure loudness in active 100 ms windows rather than long silent gaps."""
    if not samples.size:
        return 0.0
    frame_count = (samples.size + LEVEL_FRAME_SAMPLES - 1) // LEVEL_FRAME_SAMPLES
    padded = np.pad(samples, (0, frame_count * LEVEL_FRAME_SAMPLES - samples.size))
    frames = padded.reshape(frame_count, LEVEL_FRAME_SAMPLES)
    frame_levels = np.sqrt(np.mean(frames * frames, axis=1))
    active_count = max(1, int(np.ceil(frame_count * 0.1)))
    active_levels = np.partition(frame_levels, -active_count)[-active_count:]
    return float(np.mean(active_levels))


def _write_status(status_path, phase, source_states):
    if not status_path:
        return
    payload = {
        "phase": phase,
        "sources": [
            {key: state[key] for key in ("name", "kind", "ready", "level", "error")}
            for state in source_states
        ],
    }
    # The UI polls this file while capture is running. Replacing it atomically
    # with os.replace can fail on Windows when the UI briefly has the old file
    # open, ending capture with WinError 5. A partial JSON read is harmless:
    # the UI ignores it and retries on its next poll.
    with open(status_path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle)
        handle.flush()


def capture_audio(output_path, stop_path, status_path=None):
    microphones = sc.all_microphones(include_loopback=True)
    physical_mics = [mic for mic in microphones if not mic.isloopback]
    try:
        default_microphone = sc.default_microphone()
    except Exception:
        default_microphone = None
    try:
        default_speaker = sc.default_speaker()
    except Exception:
        default_speaker = None
    playback_sources = [mic for mic in microphones if mic.isloopback]
    # Teams and other apps can use a non-default output device, so capture all
    # Windows playback endpoints and prioritize the current default endpoint.
    if default_microphone is not None:
        physical_mics.sort(key=lambda mic: mic.id != default_microphone.id)
    if default_speaker is not None:
        playback_sources.sort(key=lambda mic: mic.id != default_speaker.id)
    sources = physical_mics + playback_sources
    if not sources:
        raise RuntimeError("Windows reported no microphone or playback devices")

    stop_event = threading.Event()
    chunks_by_source = []
    source_states = []
    errors = []
    readers = []
    for microphone in sources:
        chunks = []
        state = {"name": microphone.name,
                 "kind": "call" if microphone.isloopback else "mic",
                 "preferred": ((microphone.isloopback and default_speaker is not None and microphone.id == default_speaker.id)
                              or (not microphone.isloopback and default_microphone is not None and microphone.id == default_microphone.id)),
                 "ready": False, "level": 0.0, "error": None}
        chunks_by_source.append((microphone, chunks))
        source_states.append(state)
        reader = threading.Thread(target=_record_source,
                                  args=(microphone, stop_event, chunks, state, errors), daemon=True)
        readers.append(reader)
        reader.start()

    _write_status(status_path, "starting", source_states)

    try:
        deadline = time.monotonic() + 8
        next_startup_update = time.monotonic()
        while (
            not any(state["ready"] for state in source_states)
            and time.monotonic() < deadline
            and not os.path.exists(stop_path)
        ):
            if time.monotonic() >= next_startup_update:
                _write_status(status_path, "starting", source_states)
                next_startup_update = time.monotonic() + 0.25
            time.sleep(0.05)
        if not any(state["ready"] for state in source_states):
            if os.path.exists(stop_path):
                raise RuntimeError("Capture was stopped before an audio device became ready")
            raise RuntimeError("No audio device could be opened: " + "; ".join(errors))
        started = time.monotonic()
        next_status_update = started
        while not os.path.exists(stop_path) and time.monotonic() - started < MAX_SECONDS:
            if time.monotonic() >= next_status_update:
                _write_status(status_path, "listening", source_states)
                next_status_update = time.monotonic() + 0.25
            time.sleep(0.05)
    finally:
        stop_event.set()
        for reader in readers:
            reader.join(timeout=3)

    _write_status(status_path, "processing", source_states)

    tracks = []
    for (microphone, chunks), state in zip(chunks_by_source, source_states):
        if not chunks:
            continue
        samples, start_time = _mono_16k(chunks)
        if samples.size:
            level = _active_rms(samples)
            tracks.append((samples, start_time, level, microphone.name, state["kind"], state["preferred"]))

    if not tracks:
        raise RuntimeError("Microphones and Windows playback returned no audio samples. " + "; ".join(errors))
    # Keep the clearest available mic and call output as separate categories;
    # mixing every endpoint lets inactive devices add noise and duplicate speech.
    selected_tracks = []
    for kind in ("mic", "call"):
        candidates = [track for track in tracks if track[4] == kind and track[2] >= MIN_SIGNAL_RMS]
        if candidates:
            loudest = max(candidates, key=lambda track: track[2])
            preferred = next((track for track in candidates if track[5]), None)
            selected_tracks.append(
                preferred
                if preferred and preferred[2] >= loudest[2] * PREFERRED_TRACK_MIN_RATIO
                else loudest
            )
    if not selected_tracks:
        raise RuntimeError("No usable mic or call audio signal was captured. Check mute, volume, and Teams output device.")

    origin = min(track[1] for track in selected_tracks)
    end = max(round((start - origin) * TARGET_RATE) + len(samples)
              for samples, start, _, _, _, _ in selected_tracks)
    mixed = np.zeros(end, dtype=np.float32)
    contributors = np.zeros(end, dtype=np.uint8)
    selected_names = []
    for track_samples, start, track_level, name, kind, _preferred in selected_tracks:
        offset = max(0, round((start - origin) * TARGET_RATE))
        finish = min(end, offset + len(track_samples))
        if finish > offset:
            gain = min(4.0, TARGET_TRACK_RMS / max(track_level, MIN_SIGNAL_RMS))
            mixed[offset:finish] += track_samples[:finish - offset] * gain
            contributors[offset:finish] += 1
            selected_names.append(("Mic" if kind == "mic" else "Call audio") + f": {name}")
    active = contributors > 0
    mixed[active] /= np.sqrt(contributors[active].astype(np.float32))
    samples = mixed
    level = float(np.sqrt(np.mean(samples ** 2)))
    source_name = " + ".join(selected_names)
    samples = np.clip(samples, -1.0, 1.0)
    pcm = (samples * 32767).astype(np.int16)
    with wave.open(output_path, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(TARGET_RATE)
        wav.writeframes(pcm.tobytes())
    _write_status(status_path, "captured", source_states)
    return {
        "source": source_name,
        "input_level": level,
        "seconds": len(samples) / TARGET_RATE,
    }


def _emit_event(event):
    print(json.dumps(event, ensure_ascii=False), flush=True)


def serve():
    _emit_event({"event": "ready"})
    for line in sys.stdin:
        try:
            request = json.loads(line)
        except json.JSONDecodeError as error:
            _emit_event({"event": "capture_error", "error": f"Invalid capture request: {error}"})
            continue
        if not isinstance(request, dict):
            _emit_event({"event": "capture_error", "error": "Capture request must be a JSON object"})
            continue
        if request.get("command") == "close":
            return
        if request.get("command") != "capture":
            _emit_event({"event": "capture_error", "error": "Unknown capture worker command"})
            continue
        try:
            result = capture_audio(
                request["output_path"],
                request["stop_path"],
                request.get("status_path"),
            )
        except Exception as error:
            _emit_event({"event": "capture_error", "error": str(error)})
        else:
            _emit_event({"event": "captured", **result})


def main():
    if len(sys.argv) == 2 and sys.argv[1] == "--serve":
        serve()
        return
    if len(sys.argv) not in (3, 4):
        raise SystemExit(
            "Usage: capture_worker.py output.wav stop.signal [status.json] | --serve"
        )
    output_path, stop_path = sys.argv[1:3]
    status_path = sys.argv[3] if len(sys.argv) == 4 else None
    result = capture_audio(output_path, stop_path, status_path)
    _emit_event(result)


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"Audio capture worker error: {error}", file=sys.stderr)
        traceback.print_exc()
        raise SystemExit(1)
