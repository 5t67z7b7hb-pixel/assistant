# UI Dependency Trees

## Assistant window

Entry: `app.py`

Dependencies:
- `main.py`
  - `technical_glossary.py`
  - `capture_worker.py` (runtime subprocess)
  - `transcribe_worker.py` (runtime subprocess)
  - `ai_response.py`
- Native `tkinter` widgets (no project UI component dependencies)

The rendered window is created in `LightningStealthAssistant.setup_ui`: a frameless header, a 42/58 detected-question and scrollable-answer split pane, and a footer with microphone/clear controls, configured model, status, and typed-question entry. `app.py` is the only app entry point; there are no routes or browser pages.
