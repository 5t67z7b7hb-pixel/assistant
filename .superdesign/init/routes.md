# Routes

This is a single-window desktop application, not a routed web application.

## Assistant window

- Entry point: `app.py`
- Window implementation: `LightningStealthAssistant` in `main.py`
- Route: None
- Layout: `LightningStealthAssistant.setup_ui`

```python
"""Compatibility launcher for the maintained assistant implementation in main.py."""
import tkinter as tk

from main import LightningStealthAssistant


if __name__ == "__main__":
    root = tk.Tk()
    app = LightningStealthAssistant(root)
    root.mainloop()
```
