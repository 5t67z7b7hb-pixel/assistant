import tempfile
import threading
import unittest
from pathlib import Path
from types import SimpleNamespace

import webview

from main import (
    AssistantWebApi,
    WebViewUI,
    _initial_window_size,
    _taskbar_hidden_window_style,
)


class FakeWindow:
    def __init__(self):
        self.scripts = []
        self.script_ready = threading.Event()

    def evaluate_js(self, script):
        self.scripts.append(script)
        self.script_ready.set()


class WebViewUiTests(unittest.TestCase):
    def test_bundled_ui_matches_the_desktop_draft_without_network_assets(self):
        html_path = Path(__file__).resolve().parents[1] / "ui" / "index.html"
        html = html_path.read_text(encoding="utf-8")

        for element_id in (
            "mic-button",
            "close-button",
            "question-text",
            "answer-text",
            "clear-button",
            "docs-button",
            "prompt-input",
            "answer-button",
            "docs-backdrop",
            "docs-add",
            "docs-remove",
        ):
            with self.subTest(element_id=element_id):
                self.assertIn(f'id="{element_id}"', html)
        self.assertIn("@keyframes equalize", html)
        self.assertIn("prefers-reduced-motion", html)
        self.assertNotIn("https://", html)

    def test_webview_updates_are_json_encoded_and_dispatched_after_ready(self):
        window = FakeWindow()
        ui = WebViewUI()
        ui.attach(window)
        ui.update_element("status-text", {"text": "Ready: <script>"})
        ui.ready()

        self.assertTrue(window.script_ready.wait(timeout=2))
        self.assertIn("Ready: <script>", window.scripts[0])

        ui.close()

    def test_screen_sizing_preserves_the_compact_layout(self):
        self.assertEqual((520, 640), _initial_window_size(1920, 1080))
        self.assertEqual((368, 400), _initial_window_size(400, 420))

    def test_windows_taskbar_style_uses_a_tool_window(self):
        style = _taskbar_hidden_window_style(0x00040000 | 0x00000001)

        self.assertTrue(style & 0x00000080)
        self.assertFalse(style & 0x00040000)
        self.assertTrue(style & 0x00000001)

    def test_document_api_imports_lists_and_removes_local_documents(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            source = root / "guide.md"
            source.write_text("Use local documentation.", encoding="utf-8")
            library = root / "library"
            window = SimpleNamespace(
                create_file_dialog=lambda *args, **kwargs: [str(source)]
            )
            assistant = SimpleNamespace(
                document_directory=library,
                window=window,
                _refresh_document_count=lambda: None,
            )
            api = AssistantWebApi(assistant)

            imported = api.choose_and_import_documents()
            self.assertEqual("Added 1 document(s).", imported["message"])
            self.assertEqual(["guide.md"], [item["name"] for item in imported["documents"]])

            removed = api.remove_documents(["guide.md"])
            self.assertEqual("Removed 1 document(s).", removed["message"])
            self.assertEqual([], removed["documents"])

    def test_document_api_rejects_untrusted_paths(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            assistant = SimpleNamespace(
                document_directory=Path(temporary_directory),
                window=SimpleNamespace(),
                _refresh_document_count=lambda: None,
            )

            result = AssistantWebApi(assistant).remove_documents(["../outside.txt"])

        self.assertTrue(result["error"])
        self.assertEqual([], result["documents"])

    def test_webview_dialog_uses_the_current_open_file_constant(self):
        self.assertEqual(10, webview.FileDialog.OPEN)

    def test_js_api_hides_assistant_graph_from_pywebview_discovery(self):
        assistant = SimpleNamespace()
        api = AssistantWebApi(assistant)

        self.assertIs(api._assistant, assistant)
        self.assertEqual(
            {
                "ready",
                "fit_to_screen",
                "toggle_recording",
                "submit_question",
                "clear_content",
                "show_assistant",
                "close_app",
                "list_documents",
                "choose_and_import_documents",
                "remove_documents",
            },
            {name for name in dir(api) if not name.startswith("_")},
        )


if __name__ == "__main__":
    unittest.main()
