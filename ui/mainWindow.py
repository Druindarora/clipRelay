import tkinter as tk
from utils.userSettings import load_user_settings, save_user_settings
from ui.menuBar import add_menu
from ui.normalView import initialiser_vue_normale
from ui.magicView import initialiser_vue_magic
from ui.podcastView import initialiser_vue_podcast
from config import config
from services.audioService import prepare_new_recording

def apply_dark_mode(widget):
    dark_bg = "#222222"
    dark_fg = "#f0f0f0"
    for child in widget.winfo_children():
        if isinstance(child, (tk.Button, tk.Label, tk.Text, tk.Frame)):
            try:
                child.configure(bg=dark_bg, fg=dark_fg)
            except Exception:
                pass
            if isinstance(child, tk.Frame):
                try:
                    child.configure(bg=dark_bg)
                except Exception:
                    pass
            apply_dark_mode(child)
    try:
        widget.configure(bg=dark_bg)
    except Exception:
        pass

def switch_mode(root, recorder, audio_state, mode):
    """
    Bascule vers le mode 1 = normal, 2 = phrase magique, 3 = podcast.
    """
    if mode == 1:
        initialiser_vue_normale(root)
    elif mode == 2:
        initialiser_vue_magic(root)
    elif mode == 3:
        initialiser_vue_podcast(root)
    else:
        print(f"[ClipRelay] Mode inconnu : {mode}")
    apply_dark_mode(root)

def create_popup():
    root = tk.Tk()
    root.title("ClipRelay")
    root.iconbitmap("img/ClipRelay.ico")

    root.model_ready = False  # Important pour le raccourci clavier

    # Toujours démarrer en mode normal (1)
    initialiser_vue_normale(root)

    add_menu(root, changer_modele_whisper)
    apply_dark_mode(root)

    return root

def changer_modele_whisper(modele, root, record_btn, copy_prefix_btn, send_chatgpt_btn, show_vscode_btn):
    import services.audioService
    modele_court = modele.split("-")[-1]

    for widget in [record_btn, copy_prefix_btn, send_chatgpt_btn, show_vscode_btn]:
        widget.config(state=tk.DISABLED)

    root.status_label.config(text=f"Chargement du modèle {modele_court}...", fg="orange")
    print(f"[ClipRelay] Chargement du modèle {modele_court}")

    def load_and_reenable():
        services.audioService.load_whisper_model(modele)
        root.status_label.config(text=f"Modèle {modele_court} chargé !", fg="green")
        root.modele_var.set(f"Modèle : {modele_court}")
        print(f"[ClipRelay] Modèle Whisper chargé : {modele_court}")
        settings = load_user_settings()
        settings["modele"] = modele
        save_user_settings(settings)
        for widget in [record_btn, copy_prefix_btn, send_chatgpt_btn, show_vscode_btn]:
            widget.config(state=tk.NORMAL)
        root.status_label.config(text="Modèle chargé et prêt à l’emploi", fg="green")
        root.model_ready = True
        print("[ClipRelay] ✅ Initialisation complète : modèle Whisper prêt.")

    import threading
    threading.Thread(target=load_and_reenable).start()

prepare_new_recording("enregistrement.wav")
