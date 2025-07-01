import pygetwindow as gw
import keyboard
import time
import pyperclip
import threading
from utils.countdown import run_countdown

# Constants for configuration
VSCODE_WINDOW_TITLE = "Visual Studio Code"
DEFAULT_COUNTDOWN_MESSAGE = "Attention, vous avez {n} seconde(s) pour vous focus sur VS Code..."

# Utility functions

def get_active_window_title():
    """
    Get the title of the currently active window.

    Returns:
        str or None: The title of the active window, or None if no window is active.
    """
    win = gw.getActiveWindow()
    if win:
        return win.title
    return None

def activate_window_by_title(window_title):
    """
    Activate a window by its title.

    Args:
        window_title (str): The title of the window to activate.

    Returns:
        bool: True if the window was activated successfully, False otherwise.
    """
    windows = gw.getWindowsWithTitle(window_title)
    if windows:
        win = windows[0]
        win.activate()
        return True
    return False

# Refactored functions

def focus_and_paste_in_vscode(text, config, status_callback=None, countdown_callback=None):
    """
    Focus on the VS Code window and paste text into it.

    Args:
        text (str): The text to paste.
        config (dict): Configuration dictionary with timeouts and countdown settings.
        status_callback (callable, optional): Callback for status updates.
        countdown_callback (callable, optional): Callback for countdown updates.
    """
    def countdown_and_focus():
        try:
            pyperclip.copy(text)
            time.sleep(0.05)

            if activate_window_by_title(VSCODE_WINDOW_TITLE):
                time.sleep(config['timeouts']['window_switch'])
                countdown_seconds = config.get('focus_countdown', 5)
                run_countdown(
                    countdown_seconds,
                    DEFAULT_COUNTDOWN_MESSAGE,
                    countdown_callback
                )

                active_title = get_active_window_title()
                if active_title and VSCODE_WINDOW_TITLE in active_title:
                    keyboard.send('ctrl+v')
                    time.sleep(config['timeouts']['paste_delay'])
                    keyboard.send('enter')
                    if status_callback:
                        status_callback("Texte collé et envoyé dans VS Code", True)
                else:
                    if status_callback:
                        status_callback("Le focus n'est pas sur VS Code !", False)
            else:
                if status_callback:
                    status_callback("VS Code non trouvé", False)
        except Exception as e:
            if status_callback:
                status_callback(f"Erreur lors de l'exécution : {e}", False)

    threading.Thread(target=countdown_and_focus).start()

def focus_vscode(root):
    """
    Focus on the VS Code window and paste text into it.

    Args:
        root (Tkinter.Tk): The root window of the Tkinter application.
            Doit contenir un attribut `text_area` pour récupérer le texte à coller,
            et un attribut `status_label` pour afficher le statut de l'opération.
    """
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