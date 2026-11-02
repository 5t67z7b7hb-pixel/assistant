# App Layout

## LightningStealthAssistant window

- Source: `main.py:387-706`
- Framework: Native Tkinter desktop window; `app.py` launches `LightningStealthAssistant`.
- Layout: Frameless, draggable dark panel with an orange outline; lightning/status header; split detected-question and scrollable-answer panes; footer microphone/clear actions, local-model label, shortcut, status detail, and typed-question entry.
- Theme: Espresso surfaces, warm ivory text, orange/yellow accents, and brown dividers; Inter with Segoe UI fallback.
- Implementation: `LightningStealthAssistant.setup_ui`, render helpers, `_animate_equalizer`, and window-drag helpers in `main.py:387-706`.
