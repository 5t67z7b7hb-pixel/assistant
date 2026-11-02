import subprocess
import sys

def build():
    print("Building Voice Assistant for macOS with PyInstaller...")
    
    # Install PyInstaller
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Run PyInstaller configured for macOS
    cmd = [
        "pyinstaller",
        "--noconsole",
        "--windowed",
        "--name=VoiceAssistantSetup",
        "--add-data", "capture_worker.py:.",
        "--add-data", "transcribe_worker.py:.",
        "--add-data", "Modelfile:.",
        "main.py"
    ]
    
    print("Running:", " ".join(cmd))
    subprocess.check_call(cmd)
    print("Build complete!")

if __name__ == "__main__":
    build()