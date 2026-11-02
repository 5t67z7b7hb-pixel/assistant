import unittest
from pathlib import Path


class WindowsInstallerTests(unittest.TestCase):
    def test_installer_validates_and_launches_the_current_source_bundle(self):
        root = Path(__file__).resolve().parents[1]
        installer = (root / "install_and_run.ps1").read_text(encoding="utf-8")

        for required_file in (
            "app.py",
            "main.py",
            "capture_worker.py",
            "transcribe_worker.py",
            "ui\\index.html",
            "requirements.txt",
            "Modelfile",
            "qwen3-4b-instruct-2507-q4_K_M.gguf",
        ):
            with self.subTest(required_file=required_file):
                self.assertIn(f"'{required_file}'", installer)

        self.assertIn("import capture_worker, transcribe_worker, webview", installer)
        self.assertIn("$appPath = Join-Path $root 'app.py'", installer)
        self.assertIn("Start-Process -FilePath $pythonwExe", installer)
        self.assertIn("$assistantProcess.WaitForExit(8000)", installer)


if __name__ == "__main__":
    unittest.main()
