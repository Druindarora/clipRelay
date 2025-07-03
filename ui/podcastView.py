import tkinter as tk
from tkinter import filedialog
import services.podcastService as podcastService

# Fonction principale pour créer la vue podcast
def create_podcast_view(root):
    for widget in root.winfo_children():
        widget.destroy()

    # Réinitialise la fenêtre
    root.title("Mode Podcast")

    # --- Label principal ---
    label = tk.Label(root, text="🎙️ Mode podcast activé", font=("Arial", 14, "bold"), fg="green")
    label.grid(row=0, column=0, columnspan=3, pady=(10, 20))

    # --- Sélection du dossier podcast ---
    def select_podcast_folder():
        folder = filedialog.askdirectory(title="Choisir le dossier Podcast")
        if folder:
            podcastService.set_podcast_folder(folder)
            folder_label.config(text=f"Dossier podcast : {folder}")
            refresh_podcast_list()

    folder_button = tk.Button(root, text="📁 Choisir dossier podcast", command=select_podcast_folder)
    folder_button.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

    folder_label = tk.Label(root, text="Aucun dossier podcast sélectionné", fg="blue")
    folder_label.grid(row=1, column=1, columnspan=2, padx=10, pady=5, sticky="w")

    # --- Bouton lancer serveur ---
    def launch_server():
        ok = podcastService.launch_server()
        server_status_label.config(
            text="✅ Serveur en ligne sur http://localhost:8000" if ok else "❌ Échec du lancement serveur",
            fg="green" if ok else "red"
        )

    server_button = tk.Button(root, text="▶️ Lancer le serveur", command=launch_server)
    server_button.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

    server_status_label = tk.Label(root, text="Serveur non démarré", fg="gray")
    server_status_label.grid(row=2, column=1, columnspan=2, padx=10, pady=5, sticky="w")

    # --- Entrée pour URL podcast ---
    def add_url():
        url = url_entry.get()
        if url:
            ok = podcastService.process_url(url)
            url_status_label.config(
                text="✅ Podcast ajouté avec succès" if ok else "❌ Échec de l'ajout du podcast",
                fg="green" if ok else "red"
            )
            refresh_podcast_list()

    url_entry = tk.Entry(root, width=60)
    url_entry.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky="ew")

    url_button = tk.Button(root, text="➕ Ajouter URL", command=add_url)
    url_button.grid(row=3, column=2, padx=10, pady=5, sticky="ew")

    url_status_label = tk.Label(root, text="", fg="blue")
    url_status_label.grid(row=4, column=0, columnspan=3, padx=10, pady=5)

    # --- Liste des podcasts ---
    podcast_listbox = tk.Listbox(root, width=80, height=10)
    podcast_listbox.grid(row=5, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

    def refresh_podcast_list():
        podcast_listbox.delete(0, tk.END)
        podcasts = podcastService.read_rss_feed()
        for podcast in podcasts:
            podcast_listbox.insert(tk.END, f"• {podcast['title']}")

    if podcastService.get_podcast_folder():
        refresh_podcast_list()

    # --- Ajustements pour expansion ---
    root.grid_rowconfigure(5, weight=1)
    root.grid_columnconfigure(1, weight=1)
