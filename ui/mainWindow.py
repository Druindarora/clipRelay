import tkinter as tk
import threading
import time
import os
from config import MAGIC_PHRASES, config
from services.audioService import AudioRecorder, prepare_new_recording, load_whisper_model
from utils.textProcessing import nettoyer_texte_transcription  # Correction de l'import
from utils.userSettings import load_user_settings, save_user_settings
from ui.menuBar import add_menu
from ui.buttons import createButtons
from ui.stateManager import StateManager  # <-- Nouvel import

# Variable globale pour le modèle sélectionné
selected_modele = None

def apply_dark_mode(widget):
    """
    Applique un thème sombre à tous les widgets enfants.

    Args:
        widget (Tk): Le widget racine dont les enfants recevront le thème sombre.

    Returns:
        None
    """
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
                    child.configure(bg=dark_bg)  # Utilise dark_bg au lieu de accent
                except Exception:
                    pass
            apply_dark_mode(child)
    try:
        widget.configure(bg=dark_bg)
    except Exception:
        pass

def create_status_label(root):
    """
    Crée et retourne le label de statut.

    Args:
        root (Tk): La fenêtre principale.

    Returns:
        Label: Le label de statut.
    """
    status_label = tk.Label(root, text="", fg="red")
    status_label.pack(pady=(10, 5))
    return status_label

def create_countdown_label(root):
    """
    Crée et retourne le label de compte à rebours.

    Args:
        root (Tk): La fenêtre principale.

    Returns:
        Label: Le label de compte à rebours.
    """
    countdown_label = tk.Label(root, text="", fg="red", font=("Arial", 12, "bold"))
    countdown_label.pack()
    return countdown_label

def create_text_area(root):
    """
    Crée et retourne la zone de texte.

    Args:
        root (Tk): La fenêtre principale.

    Returns:
        Text: La zone de texte.
    """
    text_area = tk.Text(root, wrap=tk.WORD, insertbackground="white")
    text_area.pack(expand=True, fill=tk.BOTH, padx=10, pady=(20, 10))
    return text_area

def create_buttons(root, recorder, audio_state, mode):
    """
    Crée et configure les boutons de l'application.

    Args:
        root (Tk): La fenêtre principale.
        recorder (AudioRecorder): L'objet enregistreur audio.
        audio_state (dict): L'état audio actuel.
        mode (int): Le mode à appliquer (1 = normal, 2 = anti-pollution).

    Returns:
        list: Liste des boutons créés.
    """
    from ui.buttons import createButtons
    return createButtons(root, recorder, audio_state, mode=mode)

def configure_labels(root):
    """
    Configure les labels principaux de l'application.

    Args:
        root (Tk): La fenêtre principale.

    Returns:
        dict: Dictionnaire contenant les labels configurés.
    """
    labels = {
        "status_label": create_status_label(root),
        "countdown_label": create_countdown_label(root)
    }
    return labels

def create_popup():
    """
    Crée la fenêtre principale de l'application ClipRelay.

    Returns:
        Tk: La fenêtre principale avec tous les composants initialisés.
    """
    user_settings = load_user_settings()
    root = tk.Tk()
    root.title("ClipRelay")

    root.timer_var = tk.StringVar(value="00:00")
    root.transcription_time_var = tk.StringVar(value="Temps de transcription : --")

    # Ajout de l'icône personnalisée
    root.iconbitmap("img/ClipRelay.ico")

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
    magic_word_label = tk.Label(
        root,
        text=f"Mot magique (en medium minimum) : {MAGIC_PHRASES[0]}",
        font=("Arial", 10, "italic"),
        fg="blue"
    )
    magic_word_label.pack(pady=(0, 10))

    root.text_area = create_text_area(root)

    recorder = AudioRecorder()
    audio_state = {"recording": False, "file_exists": False}
    root.recorder = recorder
    root.audio_state = audio_state

    labels = configure_labels(root)
    root.status_label = labels["status_label"]
    root.countdown_label = labels["countdown_label"]

    # Initialisation de StateManager
    state_manager = StateManager(root)
    root.state_manager = state_manager

    mode = 1
    root.buttons = create_buttons(root, recorder, audio_state, mode)

    threading.Thread(target=lambda: changer_modele_whisper(
        modele_court,
        root,
        root.record_btn,
        root.copy_prefix_btn,
        root.send_chatgpt_btn,
        root.show_vscode_btn
    )).start()

    add_menu(root, changer_modele_whisper)

    # --- Applique le dark mode juste avant de retourner la fenêtre ---
    apply_dark_mode(root)

    return root

def refresh_buttons(root, recorder, audio_state):
    """
    Rafraîchit la zone des boutons en recréant les boutons selon le mode actuel.

    Args:
        root (Tk): La fenêtre principale.
        recorder (AudioRecorder): L'objet enregistreur audio.
        audio_state (dict): L'état audio actuel.

    Returns:
        None
    """
    if hasattr(root, "buttons_zone"):
        root.buttons_zone.destroy()
        delattr(root, "buttons_zone")
    from ui.buttons import createButtons
    from utils.userSettings import load_user_settings
    mode = load_user_settings().get("mode", 1)
    createButtons(root, recorder, audio_state, mode=mode)

def switch_mode(root, recorder, audio_state, mode):
    """
    Change le mode de l'application entre normal et anti-pollution.

    Args:
        root (Tk): La fenêtre principale.
        recorder (AudioRecorder): L'objet enregistreur audio.
        audio_state (dict): L'état audio actuel.
        mode (int): Le mode à appliquer (1 = normal, 2 = anti-pollution).

    Returns:
        None
    """
    createButtons(root, recorder, audio_state, mode)
    if mode == 2:
        # Affiche les phrases magiques en mode 2
        root.text_area.delete("1.0", "end")
        root.text_area.insert("1.0", "\n".join(MAGIC_PHRASES))
        # Ajoute une bordure rouge
        root.text_area.config(highlightthickness=2, highlightbackground="red", highlightcolor="red")
    else:
        root.text_area.delete("1.0", "end")
        # Remet la bordure à la normale
        root.text_area.config(highlightthickness=1, highlightbackground="grey", highlightcolor="grey")
    # Réappliquer le thème sombre à tout le root
    apply_dark_mode(root)

def changer_modele_whisper(modele, root, record_btn, copy_prefix_btn, send_chatgpt_btn, show_vscode_btn):
    """
    Change le modèle Whisper utilisé pour la transcription.

    Args:
        modele (str): Le nom du modèle Whisper à charger.
        root (Tk): La fenêtre principale.
        record_btn (Button): Bouton pour démarrer/arrêter l'enregistrement.
        copy_prefix_btn (Button): Bouton pour copier le préfixe.
        send_chatgpt_btn (Button): Bouton pour envoyer à ChatGPT.
        show_vscode_btn (Button): Bouton pour afficher dans VS Code.

    Returns:
        None
    """
    import services.audioService
    modele_court = modele.split("-")[-1]  # Exemple pour extraire la partie après le tiret
    for widget in [record_btn, copy_prefix_btn, send_chatgpt_btn, show_vscode_btn]:
        widget.config(state=tk.DISABLED)
    root.status_label.config(text=f"Chargement du modèle {modele_court}...", fg="orange")
    print(f"[ClipRelay] Chargement du modèle {modele_court}")
    def load_and_reenable():
        services.audioService.load_whisper_model(modele)
        root.status_label.config(text=f"Modèle {modele_court} chargé !", fg="green")
        root.modele_var.set(f"Modèle : {modele_court}")
        print(f"[ClipRelay] Modèle Whisper chargé : {modele_court}")
        # Sauvegarde du modèle choisi
        settings = load_user_settings()
        settings["modele"] = modele
        save_user_settings(settings)
        # Activer tous les boutons
        for widget in [record_btn, copy_prefix_btn, send_chatgpt_btn, show_vscode_btn]:
            widget.config(state=tk.NORMAL)

        # 🔽 ICI : Signaler que tout est prêt
        print("[ClipRelay] ✅ Initialisation complète : modèle Whisper prêt.")
        root.status_label.config(text="Modèle chargé et prêt à l’emploi", fg="green")
        root.model_ready = True  # 🔐 Flag logique pour le raccourci clavier

    threading.Thread(target=load_and_reenable).start()



prepare_new_recording("enregistrement.wav")