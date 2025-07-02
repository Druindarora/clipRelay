import tkinter as tk
from tkinter import filedialog
from utils.userSettings import load_user_settings, save_user_settings

def create_podcast_view(root):
    """
    Crée la vue pour le mode Podcast.
    """
    # Efface l'interface existante
    for widget in root.winfo_children():
        widget.destroy()

    # Titre principal
    title_label = tk.Label(root, text="🎙️ Mode Podcast activé", font=("Arial", 14, "bold"), fg="orange")
    title_label.pack(pady=(20, 10))

    # État du serveur
    root.server_status_var = tk.StringVar(value="❌ Serveur non lancé")
    server_status_label = tk.Label(root, textvariable=root.server_status_var, fg="red")
    server_status_label.pack(pady=(5, 5))

    # Bouton de lancement du serveur
    def lancer_serveur_placeholder():
        root.server_status_var.set("✅ Serveur lancé (simulé)")
        server_status_label.config(fg="green")

    start_server_btn = tk.Button(root, text="Lancer le serveur", command=lancer_serveur_placeholder)
    start_server_btn.pack(pady=(0, 20))

    # Dossiers : RSS et MP3
    user_settings = load_user_settings()
    default_rss = user_settings.get("rss_folder", "./rss")
    default_mp3 = user_settings.get("mp3_folder", "./audio")

    def choose_folder(label_var, key):
        folder = filedialog.askdirectory()
        if folder:
            label_var.set(folder)
            user_settings[key] = folder
            save_user_settings(user_settings)

    # RSS folder
    rss_var = tk.StringVar(value=default_rss)
    tk.Label(root, text="Dossier RSS :").pack()
    tk.Label(root, textvariable=rss_var, fg="blue").pack()
    tk.Button(root, text="Changer", command=lambda: choose_folder(rss_var, "rss_folder")).pack(pady=(0, 10))

    # MP3 folder
    mp3_var = tk.StringVar(value=default_mp3)
    tk.Label(root, text="Dossier MP3 :").pack()
    tk.Label(root, textvariable=mp3_var, fg="blue").pack()
    tk.Button(root, text="Changer", command=lambda: choose_folder(mp3_var, "mp3_folder")).pack(pady=(0, 20))

    # Champ d'ajout de lien
    tk.Label(root, text="Ajouter un lien vers un épisode (YouTube, MP3, etc.) :").pack()
    link_entry = tk.Entry(root, width=60)
    link_entry.pack(pady=5)

    def ajouter_episode_placeholder():
        url = link_entry.get().strip()
        if url:
            print(f"[Podcast] 🔗 Lien reçu : {url}")
            root.status_label.config(text=f"Lien reçu : {url}", fg="green")
            link_entry.delete(0, tk.END)

    tk.Button(root, text="Ajouter", command=ajouter_episode_placeholder).pack(pady=(5, 10))

    # Label de statut général
    if hasattr(root, "status_label"):
        label = tk.Label(root, text="Mode podcast prêt à l'emploi.", fg="green", font=("Arial", 12, "bold"))
        label.pack(pady=20)

