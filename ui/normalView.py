import tkinter as tk
import threading
from services.audioService import AudioRecorder, load_whisper_model
from utils.userSettings import load_user_settings
from ui.buttons import createButtons
from ui.stateManager import StateManager
from config import MAGIC_PHRASES

def create_normal_view(root):
    """
    Initialise tous les composants visuels pour le mode normal.
    """
    # Nettoyer la fenêtre de tous les widgets (sauf barre de menu)
    for widget in root.winfo_children():
        if not isinstance(widget, tk.Menu):
            widget.destroy()

    user_settings = load_user_settings()
    modele_court = user_settings.get("modele", "small")
    duree_max = user_settings.get("duree_enregistrement", 60)


    # Variables globales pour timers
    root.timer_var = tk.StringVar(value="00:00")
    root.transcription_time_var = tk.StringVar(value="Temps de transcription : --")
    root.duree_var = tk.StringVar(value=f"Durée max : {duree_max // 60} min")

    # Label modèle
    img_model = tk.PhotoImage(file="img/model.png")
    root.img_model = img_model
    root.modele_var = tk.StringVar(value=f"Modèle : {modele_court}")
    modele_label = tk.Label(
        root,
        textvariable=root.modele_var,
        font=("Arial", 10, "bold"),
        image=img_model,
        compound="left"
    )
    modele_label.pack(pady=(10, 0))

    # Label mot magique
    magic_word_label = tk.Label(
        root,
        text=f"Mot magique (en medium minimum) : {MAGIC_PHRASES[0]}",
        font=("Arial", 10, "italic"),
        fg="blue"
    )
    magic_word_label.pack(pady=(0, 10))

    # Zone de texte
    root.text_area = tk.Text(root, wrap=tk.WORD, insertbackground="white")
    root.text_area.pack(expand=True, fill=tk.BOTH, padx=10, pady=(20, 10))

    # Labels
    root.status_label = tk.Label(root, text="Modèle chargé et prêt à l’emploi", fg="green")
    root.status_label.pack(pady=(10, 5))

    root.countdown_label = tk.Label(root, text="", fg="red", font=("Arial", 12, "bold"))
    root.countdown_label.pack()

    # Recorder
    recorder = AudioRecorder()
    root.recorder = recorder
    root.audio_state = {"recording": False, "file_exists": False}

    # State Manager
    root.state_manager = StateManager(root)

    # Boutons
    mode = 1
    root.buttons = createButtons(root, recorder, root.audio_state, mode=mode)

    # Chargement du modèle
    threading.Thread(target=lambda: load_whisper_model(modele_court)).start()
