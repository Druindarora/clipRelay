import tkinter as tk
import threading
from config import config
from services.audioService import AudioRecorder, changer_modele_whisper, prepare_new_recording, load_whisper_model
from utils.userSettings import load_user_settings, save_user_settings
from ui.menuBar import add_menu
from ui.buttons import createButtons

# Variable globale pour le modèle sélectionné
selected_modele = None

def on_configure(event, root):
    settings = load_user_settings()
    settings["geometry"] = root.geometry()
    save_user_settings(settings)

def apply_dark_mode(widget):
    """Applique un thème sombre à tous les widgets enfants."""
    dark_bg = "#222222"
    dark_fg = "#f0f0f0"
    accent = "#444444"
    for child in widget.winfo_children():
        if isinstance(child, (tk.Button, tk.Label, tk.Text, tk.Frame)):
            try:
                child.configure(bg=dark_bg, fg=dark_fg)
            except Exception:
                pass
            if isinstance(child, tk.Frame):
                try:
                    child.configure(bg=accent)
                except Exception:
                    pass
            apply_dark_mode(child)
    try:
        widget.configure(bg=dark_bg)
    except Exception:
        pass

def create_popup():
    user_settings = load_user_settings()
    root = tk.Tk()
    root.title("ClipRelay")

    # Ajout de l'icône personnalisée
    root.iconbitmap("img/ClipRelay.ico")

    # Taille et position de la fenêtre
    width, height = config['window_size']
    geometry = user_settings.get("geometry", f"{width}x{height}")
    root.geometry(geometry)

    img_model = tk.PhotoImage(file="img/model.png")
    root.img_model = img_model  # Pour éviter le garbage collector

    modele_court = user_settings.get("modele", "small")
    root.modele_var = tk.StringVar(value=f"Modèle : {modele_court}")
    modele_label = tk.Label(
        root,
        textvariable=root.modele_var,
        font=("Arial", 10, "bold"),
        image=img_model,
        compound="left"
    )
    modele_label.pack(pady=(10, 0))

    # Ajout de l'affichage du premier mot magique
    from services.audioService import MAGIC_WORDS
    magic_word_label = tk.Label(
        root,
        text=f"Mot magique : {MAGIC_WORDS[0]}",
        font=("Arial", 10, "italic"),
        fg="blue"
    )
    magic_word_label.pack(pady=(0, 10))

    text_area = tk.Text(root, wrap=tk.WORD, insertbackground="white")
    text_area.pack(expand=True, fill=tk.BOTH, padx=10, pady=(20, 10))
    root.text_area = text_area

    recorder = AudioRecorder()
    audio_state = {"recording": False, "file_exists": False}
    root.recorder = recorder
    root.audio_state = audio_state

    # duree = user_settings.get("duree_enregistrement", 60)
    # minutes = duree // 60
    # root.duree_var = tk.StringVar(value=f"Durée max : {minutes} min")
    # duree_label = tk.Label(
    #     root,
    #     textvariable=root.duree_var,
    #     font=("Arial", 10, "italic")
    # )
    # duree_label.pack(pady=(0, 10))

    # Récupère le mode courant (1 = normal, 2 = anti-pollution)
    mode = user_settings.get("mode", 1)
    createButtons(root, recorder, audio_state, mode=mode)

    # La zone de message Succès/Erreur passe ici
    status_label = tk.Label(root, text="", fg="red")
    status_label.pack(pady=(10, 5))
    root.status_label = status_label

    # La zone de compte à rebours reste en bas
    root.countdown_label = tk.Label(root, text="", fg="red", font=("Arial", 12, "bold"))
    root.countdown_label.pack()  # Place-le sous les boutons
    # countdown_label = tk.Label(root, text="", fg="red")
    # countdown_label.pack(pady=(0, 20))
    # root.countdown_label = countdown_label

    threading.Thread(target=lambda: load_whisper_model(modele_court)).start()
    add_menu(root, changer_modele_whisper)
    root.bind("<Configure>", lambda event: on_configure(event, root))

    # --- Applique le dark mode juste avant de retourner la fenêtre ---
    apply_dark_mode(root)

    return root

def refresh_buttons(root, recorder, audio_state):
    if hasattr(root, "buttons_zone"):
        root.buttons_zone.destroy()
        delattr(root, "buttons_zone")
    from ui.buttons import createButtons
    from utils.userSettings import load_user_settings
    mode = load_user_settings().get("mode", 1)
    createButtons(root, recorder, audio_state, mode=mode)

def switch_mode(root, recorder, audio_state, mode):
    createButtons(root, recorder, audio_state, mode)
    if mode == 2:
        user_settings = load_user_settings()
        phrases = user_settings.get("phrases_a_supprimer", [])
        if not phrases:
            phrases = ["(Aucune phrase à supprimer)"]
        root.text_area.delete("1.0", "end")
        root.text_area.insert("1.0", "\n".join(phrases))
        # Ajoute une bordure rouge
        root.text_area.config(highlightthickness=2, highlightbackground="red", highlightcolor="red")
    else:
        root.text_area.delete("1.0", "end")
        # Remet la bordure à la normale
        root.text_area.config(highlightthickness=1, highlightbackground="grey", highlightcolor="grey")

prepare_new_recording("enregistrement.wav")