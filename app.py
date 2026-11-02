"""Compatibility launcher for the maintained assistant implementation in main.py."""
import tkinter as tk

from main import LightningStealthAssistant


if __name__ == "__main__":
    root = tk.Tk()
    app = LightningStealthAssistant(root)
    root.mainloop()
