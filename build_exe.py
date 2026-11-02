import os
import subprocess
import sys

def build():
    print("Building Voice Assistant .exe with PyInstaller...")
    
    # Ensure pyinstaller is installed
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Run PyInstaller with appropriate flags to bundle everything
    # We need main.py as the entry point, plus capture_worker.py and transcribe_worker.py as data or bundled scripts.
    # Also include Modelfile, config.ini if needed.
    
    cmd = [
        "pyinstaller",
        "--noconsole",
        "--onefile",
        "--name=VoiceAssistantSetup",
        "--add-data", "capture_worker.py;.",
        "--add-data", "transcribe_worker.py;.",
        "--add-data", "Modelfile;.",
        "main.py"
    ]
    
    print("Running:", " ".join(cmd))
    subprocess.check_call(cmd)
    print("Build complete! Check the 'dist' folder for VoiceAssistantSetup.exe")

if __name__ == "__main__":
    build()