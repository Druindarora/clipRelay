from services.vsCodeService import focus_and_paste_in_vscode
from config import config
from utils.userSettings import load_user_settings

def on_hotkey(event=None, root=None):
    mode = load_user_settings().get("mode", 1)
    if mode == 2:
        # Ignore le raccourci en mode anti-pollution
        return
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