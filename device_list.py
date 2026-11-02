"""List available audio devices using PyAudioWPatch."""

import pyaudiowpatch as pyaudio


def main():
    audio = pyaudio.PyAudio()
    try:
        for index in range(audio.get_device_count()):
            info = audio.get_device_info_by_index(index)
            print(f"{index}: {info['name']}")
    finally:
        audio.terminate()


if __name__ == '__main__':
    main()
