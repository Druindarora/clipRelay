import tkinter as tk
from utils.userSettings import load_user_settings, save_user_settings
from services.chatgptService import send_text_to_chatgpt
from services.audioService import handle_record
from services.vsCodeService import focus_and_paste_in_vscode

def create_mode1_buttons(root, recorder, audio_state):
    import pyperclip

    # Label durée max
    user_settings = load_user_settings()
    duree = user_settings.get("duree_enregistrement", 60)
    minutes = duree // 60
    root.duree_var = tk.StringVar(value=f"Durée max : {minutes} min")
    duree_label = tk.Label(
        root.buttons_zone,
        textvariable=root.duree_var,
        font=("Arial", 10, "italic")
    )
    duree_label.pack()

    # Bouton d'enregistrement
    img_start_record = tk.PhotoImage(file="img/start.png")
    img_stop_record = tk.PhotoImage(file="img/record_2.png")
    root.img_start_record = img_start_record
    root.img_stop_record = img_stop_record

    record_btn = tk.Button(
        root.buttons_zone,
        image=img_start_record,
        text="Démarrer l'enregistrement",
        compound="left",
        command=lambda: handle_record(
            root, recorder, audio_state,
            copy_prefix_btn,
            send_chatgpt_btn,
            getattr(root, "show_vscode_btn", None),
            record_btn,           # <-- On passe bien record_btn ici
            copy_pollution_btn
        )
    )
    record_btn.image = img_start_record
    record_btn.pack(pady=(10, 5))
    root.record_btn = record_btn

    # Minuteur
    root.timer_var = tk.StringVar(value="00:00")
    timer_label = tk.Label(root.buttons_zone, textvariable=root.timer_var, font=("Arial", 10))
    timer_label.pack()

    # Frame pour les autres boutons
    button_frame = tk.Frame(root.buttons_zone)
    button_frame.pack(pady=10)
    root.button_frame = button_frame

    img_pollution = tk.PhotoImage(file="img/copy.png")
    root.img_pollution = img_pollution
    copy_pollution_btn = tk.Button(
        button_frame,
        image=img_pollution,
        text="Copier pollution",
        compound="left",
        command=lambda: copy_pollution(root)
    )
    copy_pollution_btn.grid(row=0, column=0, padx=10)
    root.copy_pollution_btn = copy_pollution_btn

    # --- Les autres boutons sont décalés d'une colonne ---
    # Bouton Copier [ChatRelay]
    img_copy = tk.PhotoImage(file="img/copy.png")
    root.img_copy = img_copy
    copy_prefix_btn = tk.Button(
        button_frame,
        image=img_copy,
        text="Copier [ChatRelay]",
        compound="left",
        command=lambda: copy_chatrelay_prefix(root)
    )
    copy_prefix_btn.grid(row=0, column=1, padx=10)
    root.copy_prefix_btn = copy_prefix_btn

    # Bouton Envoyer vers ChatGPT
    img_send = tk.PhotoImage(file="img/send.png")
    root.img_send = img_send

    send_chatgpt_btn = tk.Button(
        button_frame,
        image=img_send,
        text="Envoyer vers ChatGPT",
        compound="left",
        command=lambda: handle_send_chatgpt(root)
    )
    send_chatgpt_btn.grid(row=0, column=2, padx=10)
    root.send_chatgpt_btn = send_chatgpt_btn

    # Bouton Focus VS Code
    img_focus = tk.PhotoImage(file="img/Focus.png")
    root.img_focus = img_focus

    show_vscode_btn = tk.Button(
        button_frame,
        image=img_focus,
        text="Focus VS Code",
        compound="left",
        command=lambda: focus_vscode(root)
    )
    show_vscode_btn.grid(row=0, column=3, padx=10)
    root.show_vscode_btn = show_vscode_btn

def create_mode2_buttons(root):
    # --- Bouton Sauvegarder normal ---
    def save_phrases():
        # Logique de sauvegarde à ajouter ici si besoin
        pass

    save_btn = tk.Button(
        root.buttons_zone,
        text="Sauvegarder",
        command=save_phrases
    )
    save_btn.pack(pady=10)

def createButtons(root, recorder, audio_state, mode=1):
    # Détruit la zone précédente si elle existe
    if hasattr(root, "buttons_zone"):
        root.buttons_zone.destroy()
    root.buttons_zone = tk.Frame(root)
    root.buttons_zone.pack(pady=10)

    if mode == 2:
        create_mode2_buttons(root)
    else:
        create_mode1_buttons(root, recorder, audio_state)

def focus_vscode(root):
    from config import config
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

def handle_send_chatgpt(root):
    text = root.text_area.get("1.0", "end-1c")
    send_text_to_chatgpt(
        text,
        status_callback=lambda msg, ok: root.status_label.config(text=msg, fg="green" if ok else "red"),
        root=root
    )

# --- Nouveau bouton Copier pollution ---
import pyperclip
def copy_pollution(root):
    try:
        selected_text = root.text_area.get(tk.SEL_FIRST, tk.SEL_LAST)
    except tk.TclError:
        selected_text = ""
    if selected_text:
        pyperclip.copy(selected_text)
        # Passe en mode 2 après la copie
        from utils.userSettings import load_user_settings, save_user_settings
        from ui.mainWindow import switch_mode
        settings = load_user_settings()
        settings["mode"] = 2
        save_user_settings(settings)
        switch_mode(root, root.recorder, root.audio_state, 2)
        # Met à jour le message d’état
        if root and hasattr(root, "status_label"):
            root.status_label.config(
                text="Copier la pollution à la ligne. Copier la nouvelle solution à la ligne.",
                fg="blue"
            )
    else:
        if root and hasattr(root, "status_label"):
            root.status_label.config(text="Aucune sélection à copier.", fg="red")

def copy_chatrelay_prefix(root):
    text = root.text_area.get("1.0", "end-1c")
    prefix = "[ChatRelay] "
    pyperclip.copy(prefix + text)
    if root and hasattr(root, "status_label"):
        root.status_label.config(text="Texte copié avec préfixe !", fg="green")