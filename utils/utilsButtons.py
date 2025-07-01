import tkinter as tk
import pyperclip
from utils.clipRelayError import ClipRelayError
from services.chatgptService import send_text_to_chatgpt

# --- Nouveau bouton Copier pollution ---
def copy_pollution(root):
    """
    Copie le texte sélectionné dans le presse-papiers et passe en mode anti-pollution.

    Args:
        root (Tk): La fenêtre principale contenant la zone de texte.

    Raises:
        ClipRelayError: Si aucune sélection n'est disponible.
    """
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
                fg="orange"
            )
    else:
        if root and hasattr(root, "status_label"):
            root.status_label.config(text="Aucune sélection à copier.", fg="red")
        raise ClipRelayError("Aucune sélection disponible pour la copie.")

def copy_chatrelay_prefix(root):
    """
    Copie le texte de la zone de texte avec un préfixe spécifique dans le presse-papiers.

    Args:
        root (Tk): La fenêtre principale contenant la zone de texte.

    Raises:
        ClipRelayError: Si la zone de texte est vide.
    """
    text = root.text_area.get("1.0", "end-1c")
    if not text.strip():
        if root and hasattr(root, "status_label"):
            root.status_label.config(text="La zone de texte est vide.", fg="red")
        raise ClipRelayError("La zone de texte est vide.")
    prefix = "[ChatRelay] "
    pyperclip.copy(prefix + text)
    if root and hasattr(root, "status_label"):
        root.status_label.config(text="Texte copié avec préfixe !", fg="green")
