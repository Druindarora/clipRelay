import tkinter as tk
from config import MAGIC_PHRASES
from ui.buttons import createButtons
from services.audioService import AudioRecorder
from ui.stateManager import StateManager

def create_magic_view(root):
    """
    Initialise la vue en mode Phrase magique.
    """
    # Nettoyer tous les widgets
    for widget in root.winfo_children():
        if not isinstance(widget, tk.Menu):
            widget.destroy()

    # Phrase magique affichée dans la zone texte
    root.text_area = tk.Text(root, wrap=tk.WORD, insertbackground="white")
    root.text_area.insert("1.0", "\n".join(MAGIC_PHRASES))
    root.text_area.config(highlightthickness=2, highlightbackground="red", highlightcolor="red")
    root.text_area.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

    root.status_label = tk.Label(root, text="Mode Phrase magique activé", fg="orange")
    root.status_label.pack(pady=(10, 5))

    # Enregistreur et boutons
    recorder = AudioRecorder()
    root.recorder = recorder
    root.audio_state = {"recording": False, "file_exists": False}
    root.state_manager = StateManager(root)

    root.buttons = createButtons(root, recorder, root.audio_state, mode=2)
