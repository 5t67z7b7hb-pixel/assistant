import tkinter as tk
from ctypes import windll

def create_stealth_assistant():
    root = tk.Tk()
    root.title("AI Interview Assistant")
    root.geometry("400x300")
    root.attributes("-topmost", True)  # Keep window floating on top

    # Apply Windows screen-capture exclusion on window map
    root.bind("<Map>", lambda e: windll.user32.SetWindowDisplayAffinity(root.winfo_id(), 0x00000011))

    # UI Content
    label = tk.Label(root, text="AI Assistant Ready...", fg="green", font=("Arial", 14))
    label.pack(expand=True)

    root.mainloop()

if __name__ == "__main__":
    create_stealth_assistant()
