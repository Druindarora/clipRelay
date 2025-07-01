import pyperclip
from utils.clipRelayError import ClipRelayError
    
def copy_text(root):
    """
    Copie tout le contenu de la zone de texte dans le presse-papiers.

    Args:
        root (Tk): La fenêtre principale.

    Raises:
        ClipRelayError: Si la zone de texte est vide.
    """
    text = root.text_area.get("1.0", "end-1c").strip()
    if not text:
        if root and hasattr(root, "status_label"):
            root.status_label.config(text="La zone de texte est vide.", fg="red")
        raise ClipRelayError("Impossible de copier : la zone de texte est vide.")
    
    pyperclip.copy(text)

    if root and hasattr(root, "status_label"):
        root.status_label.config(text="Texte copié dans le presse-papiers.", fg="green")

def copy_chatrelay_prefix(root):
    """
    Copie uniquement le tag [ChatRelay] dans le presse-papiers.

    Args:
        root (Tk): La fenêtre principale.
    """
    pyperclip.copy("[ChatRelay] ")
    if root and hasattr(root, "status_label"):
        root.status_label.config(text="Tag [ChatRelay] copié dans le presse-papiers !", fg="green")

