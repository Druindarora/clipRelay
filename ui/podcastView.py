import tkinter as tk

def initialiser_vue_podcast(root):
    """
    Initialise la vue pour le mode Podcast (mode 3).
    """
    for widget in root.winfo_children():
        if not isinstance(widget, tk.Menu):
            widget.destroy()

    label = tk.Label(root, text="🎙️ Mode podcast activé", fg="blue", font=("Arial", 14, "bold"))
    label.pack(pady=20)
