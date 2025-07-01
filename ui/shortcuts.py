from services.vsCodeService import focus_and_paste_in_vscode
from config import config
from utils.userSettings import load_user_settings

def on_hotkey(event=None, root=None):
    print("[DEBUG] Raccourci déclenché")

    """
    Gère le raccourci clavier pour l'enregistrement.

    Args:
        event (Event, optional): L'événement déclenché par le raccourci.
        root (Tk, optional): La fenêtre principale.

    Returns:
        None
    """

    if not hasattr(root, "model_ready") or not root.model_ready:
        print("[ClipRelay] ⛔ Modèle non prêt, raccourci ignoré.")
        if hasattr(root, "status_label"):
            root.status_label.config(text="Modèle non encore chargé. Réessayez dans un instant.", fg="red")
        return


    mode = load_user_settings().get("mode", 1)
    if mode == 2:
        # Ignore le raccourci en mode anti-pollution
        return

    if root:
        # Remet la fenêtre au premier plan et donne le focus
        root.lift()
        root.attributes('-topmost', True)
        root.focus_force()
        root.after(500, lambda: root.attributes('-topmost', False))  # Retire "always on top" après 0,5s

        # Simule le clic sur le bouton d'enregistrement
        if hasattr(root, "record_btn"):
            root.record_btn.invoke()

def focus_vscode(root=None):
    """
    Colle le texte dans VS Code et met à jour les labels de statut et de compte à rebours.

    Args:
        root (Tk, optional): La fenêtre principale.

    Returns:
        None
    """
    try:
        text = root.text_area.get("1.0", "end-1c") if root and hasattr(root, "text_area") else ""
        if not text.strip():
            if root and hasattr(root, "state_manager"):
                root.state_manager.update_status("Aucun texte à coller, focus annulé.", "red")
            return

        focus_and_paste_in_vscode(
            text,
            config,
            status_callback=lambda msg, ok: root.state_manager.update_status(msg, "green" if ok else "red") if hasattr(root, "state_manager") else None,
            countdown_callback=lambda msg: root.state_manager.update_countdown(msg, "red") if hasattr(root, "state_manager") else None
        )
    except Exception as e:
        if root and hasattr(root, "state_manager"):
            root.state_manager.update_status(f"Erreur : {e}", "red")