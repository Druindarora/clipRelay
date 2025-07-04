import tkinter as tk
from utils.userSettings import load_user_settings, save_user_settings

def update_user_settings(key, value):
    settings = load_user_settings()
    settings[key] = value
    save_user_settings(settings)

def create_dynamic_menu(root, menu_label, options, variable, update_callback):
    menu = tk.Menu(root, tearoff=0)
    for label, value in options.items():
        menu.add_radiobutton(
            label=label,
            variable=variable,
            value=value,
            command=lambda v=value: update_callback(v)
        )
    return menu

def add_menu(root, changer_modele_whisper, switch_mode_callback):
    menubar = tk.Menu(root)

    # Menu des modèles Whisper
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
        update_user_settings("modele", modele_val)
        selected_modele.set(modele_val)

    modele_menu = create_dynamic_menu(root, "Modeles", modeles, selected_modele, select_modele)
    menubar.add_cascade(label="Modeles", menu=modele_menu)

    # Menu des durées maximales d'enregistrement
    durees = {
        "1 minute": 60,
        "2 minutes": 120,
        "5 minutes": 300,
        "10 minutes": 600
    }
    duree_sauvegardee = user_settings.get("duree_enregistrement", 60)
    selected_duree = tk.IntVar(value=duree_sauvegardee)

    def select_duree(valeur):
        update_user_settings("duree_enregistrement", valeur)
        selected_duree.set(valeur)
        minutes = valeur // 60
        if hasattr(root, "duree_var"):
            root.duree_var.set(f"Durée max : {minutes} min")

    max_menu = create_dynamic_menu(root, "Temps max d'enregistrement", durees, selected_duree, select_duree)
    menubar.add_cascade(label="Temps max d'enregistrement", menu=max_menu)

    # Menu des modes
    if not hasattr(root, "mode_var"):
        root.mode_var = tk.IntVar(value=1)  # Utilise l'instance existante si elle existe

    mode_menu = tk.Menu(menubar, tearoff=0)
    mode_menu.add_radiobutton(label="Mode normal", variable=root.mode_var, value=1, command=lambda: switch_mode_callback(root, 1))
    mode_menu.add_radiobutton(label="Mode phrase magique", variable=root.mode_var, value=2, command=lambda: switch_mode_callback(root, 2))
    mode_menu.add_radiobutton(label="Mode podcast", variable=root.mode_var, value=3, command=lambda: switch_mode_callback(root, 3))

    menubar.add_cascade(label="Mode", menu=mode_menu)

    root.config(menu=menubar)
