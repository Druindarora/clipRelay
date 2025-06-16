import tkinter as tk
from utils.userSettings import load_user_settings, save_user_settings

def add_menu(root, changer_modele_whisper):
    import tkinter as tk
    from utils.userSettings import load_user_settings, save_user_settings

    def set_mode(mode):
        settings = load_user_settings()
        settings["mode"] = mode
        save_user_settings(settings)
        root.mode_var.set(mode)
        from ui.mainWindow import switch_mode  # Import local pour éviter la boucle
        switch_mode(root, root.recorder, root.audio_state, mode)

    menubar = tk.Menu(root)
    modele_menu = tk.Menu(menubar, tearoff=0)

    # Dictionnaire label affiché -> valeur du modèle
    modeles = {
        "Whisper Tiny (39Mo - Faible - Ultra rapide)": "tiny",
        "Whisper Base (74Mo - Moyen - Rapide)": "base",
        "Whisper Small (244Mo - Bon - Temps réel ou presque)": "small",
        "Whisper Medium (769Mo - Très bon - Plus lent)": "medium",
        "Whisper Large (1.55Go - Excellent - Très lent sans GPU)": "large"
    }

    user_settings = load_user_settings()
    modele_sauvegarde = user_settings.get("modele", "small")
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
    menubar.add_cascade(label="Modeles", menu=modele_menu)

    # --- Nouveau menu Max Enregistrement ---
    max_menu = tk.Menu(menubar, tearoff=0)
    duree_sauvegardee = user_settings.get("duree_enregistrement", 60)

    durees = {
        "1 minute": 60,
        "2 minutes": 120,
        "5 minutes": 300,
        "10 minutes": 600
    }
    selected_duree = tk.IntVar(value=duree_sauvegardee)

    def select_duree(valeur):
        settings = load_user_settings()
        settings["duree_enregistrement"] = valeur
        save_user_settings(settings)
        selected_duree.set(valeur)
        minutes = valeur // 60
        if hasattr(root, "duree_var"):
            root.duree_var.set(f"Durée max : {minutes} min")

    for label, value in durees.items():
        max_menu.add_radiobutton(
            label=label,
            variable=selected_duree,
            value=value,
            command=lambda v=value: select_duree(v)
        )
    menubar.add_cascade(label="Temps max d'enregistrement", menu=max_menu)

    # --- Menu Mode ---
    mode_menu = tk.Menu(menubar, tearoff=0)
    # Variable Tkinter pour le mode sélectionné
    root.mode_var = tk.IntVar(value=user_settings.get("mode", 1))
    mode_menu.add_radiobutton(label="Mode normal", variable=root.mode_var, value=1, command=lambda: set_mode(1))
    mode_menu.add_radiobutton(label="Mode anti-pollution", variable=root.mode_var, value=2, command=lambda: set_mode(2))
    menubar.add_cascade(label="Mode", menu=mode_menu)

    root.config(menu=menubar)