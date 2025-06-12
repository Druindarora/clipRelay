import tkinter as tk
import threading
import pyperclip
from config import config
from services.audioService import AudioRecorder, changer_modele_whisper, prepare_new_recording, load_whisper_model, handle_record
from services.chatgptService import send_text_to_chatgpt
from services.vsCodeService import focus_and_paste_in_vscode
from utils.userSettings import load_user_settings, save_user_settings

# Variable globale pour le modèle sélectionné
selected_modele = None

def on_configure(event, root):
    settings = load_user_settings()
    settings["geometry"] = root.geometry()
    save_user_settings(settings)

def create_popup():
    user_settings = load_user_settings()
    root = tk.Tk()
    root.title("ClipRelay")

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

    text_area = tk.Text(root, wrap=tk.WORD)
    text_area.pack(expand=True, fill=tk.BOTH, padx=10, pady=(20, 10))
    root.text_area = text_area

    recorder = AudioRecorder()
    audio_state = {"recording": False, "file_exists": False}

    # Appelle la création de tous les boutons
    createButtons(root, recorder, audio_state)

    # La zone de message Succès/Erreur passe ici
    status_label = tk.Label(root, text="", fg="red")
    status_label.pack(pady=(10, 5))
    root.status_label = status_label

    # La zone de compte à rebours reste en bas
    countdown_label = tk.Label(root, text="", fg="red")
    countdown_label.pack(pady=(0, 20))
    root.countdown_label = countdown_label

    threading.Thread(target=lambda: load_whisper_model(modele_court)).start()
    add_menu(root)
    root.bind("<Configure>", lambda event: on_configure(event, root))
    return root

def add_menu(root):
    global selected_modele
    menu_bar = tk.Menu(root)
    modele_menu = tk.Menu(menu_bar, tearoff=0)

    # Dictionnaire label affiché -> valeur du modèle
    modeles = {
        "Whisper Tiny (39Mo - Faible - Ultra rapide)": "tiny",
        "Whisper Base (74Mo - Moyen - Rapide)": "base",
        "Whisper Small (244Mo - Bon - Temps réel ou presque)": "small",
        "Whisper Medium (769Mo - Très bon - Plus lent)": "medium",
        "Whisper Large (1.55Go - Excellent - Très lent sans GPU)": "large"
    }

    # On charge le modèle sauvegardé, sinon "small"
    user_settings = load_user_settings()
    modele_sauvegarde = user_settings.get("modele", "small")

    # Variable Tkinter pour le modèle sélectionné (stocke la valeur du modèle)
    selected_modele = tk.StringVar(value=modele_sauvegarde)

    def select_modele(modele_val):
        changer_modele_whisper(
            modele_val,
            root,
            root.record_btn,
            root.copy_prefix_btn,
            root.send_chatgpt_btn,
            root.show_vscode_btn,
        )
        selected_modele.set(modele_val)

    for label, value in modeles.items():
        modele_menu.add_radiobutton(
            label=label,
            variable=selected_modele,
            value=value,
            command=lambda v=value: select_modele(v)
        )
    menu_bar.add_cascade(label="Modeles", menu=modele_menu)
    root.config(menu=menu_bar)

def copy_chatrelay_prefix():
    pyperclip.copy("[ChatRelay] ")
    print("[ClipRelay] Préfixe [ChatRelay] copié dans le presse-papiers")

def log_status(root, message, success=False):
    print(f"[ClipRelay] {message}")
    if root and hasattr(root, "status_label"):
        color = "green" if success else "red"
        root.status_label.config(text=message, fg=color)

def on_hotkey(event=None, root=None):
    # Remet la fenêtre au premier plan et donne le focus
    if root:
        root.lift()
        root.attributes('-topmost', True)
        root.focus_force()
        root.after(500, lambda: root.attributes('-topmost', False))  # Optionnel : retire le "always on top" après 0,5s
    # Simule le clic sur le bouton d'enregistrement
    if root and hasattr(root, "record_btn"):
        root.record_btn.invoke()

def focus_vscode(root=None):
    text = root.text_area.get("1.0", "end-1c") if root and hasattr(root, "text_area") else ""
    if not text.strip():
        if root and hasattr(root, "status_label"):
            root.status_label.config(text="Aucun texte à coller, focus annulé.", fg="red")
        return
    focus_and_paste_in_vscode(
        text,
        config,
        status_callback=lambda msg, ok: root.status_label.config(text=msg, fg="green" if ok else "red"),
        countdown_callback=lambda msg: root.countdown_label.config(text=msg, fg="red")
    )

def createButtons(root, recorder, audio_state):
    # --- BOUTON ENREGISTREMENT + CHRONO ---
    img_start_record = tk.PhotoImage(file="img/start.png")
    img_stop_record = tk.PhotoImage(file="img/record_2.png")
    root.img_start_record = img_start_record
    root.img_stop_record = img_stop_record

    record_btn = tk.Button(
        root,
        image=img_start_record,
        text="Démarrer l'enregistrement",
        compound="left",
        command=lambda: handle_record(
            root, recorder, audio_state,
            root.copy_prefix_btn, root.send_chatgpt_btn, root.show_vscode_btn, record_btn
        )
    )
    record_btn.image = img_start_record
    record_btn.pack(pady=(10, 5))
    root.record_btn = record_btn

    # Chronomètre juste sous le bouton d'enregistrement
    root.timer_var = tk.StringVar(value="00:00")
    timer_label = tk.Label(root, textvariable=root.timer_var, font=("Arial", 10))
    timer_label.pack()

    # Ensuite la frame pour les trois autres boutons côte à côte
    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    img_copy = tk.PhotoImage(file="img/copy.png")
    root.img_copy = img_copy  # Pour éviter le garbage collector

    copy_prefix_btn = tk.Button(
        button_frame,
        image=img_copy,
        text="Copier [ChatRelay]",
        compound="left",
        command=lambda: copy_chatrelay_prefix()
    )
    copy_prefix_btn.grid(row=0, column=0, padx=10)
    root.copy_prefix_btn = copy_prefix_btn

    img_send = tk.PhotoImage(file="img/send.png")
    root.img_send = img_send  # Pour éviter le garbage collector

    def handle_send_chatgpt():
        text = root.text_area.get("1.0", "end-1c")
        send_text_to_chatgpt(
            text,
            status_callback=lambda msg, ok: root.status_label.config(text=msg, fg="green" if ok else "red")
        )

    send_chatgpt_btn = tk.Button(
        button_frame,
        image=img_send,
        text="Envoyer vers ChatGPT",
        compound="left",
        command=handle_send_chatgpt
    )
    send_chatgpt_btn.grid(row=0, column=1, padx=10)
    root.send_chatgpt_btn = send_chatgpt_btn

    img_focus = tk.PhotoImage(file="img/Focus.png")
    root.img_focus = img_focus  # Pour éviter le garbage collector

    show_vscode_btn = tk.Button(
        button_frame,
        image=img_focus,
        text="Focus VS Code",
        compound="left",
        command=lambda: focus_vscode(root)
    )
    show_vscode_btn.grid(row=0, column=2, padx=10)
    root.show_vscode_btn = show_vscode_btn  # <-- Ajoute cette ligne

prepare_new_recording("enregistrement.wav")