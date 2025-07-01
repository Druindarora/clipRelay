import pyautogui
from config import config
from utils.countdown import run_countdown
import time
import pyperclip
import pygetwindow as gw
import requests
import threading
import tkinter as tk
from tkinter import filedialog

# Constants for configuration
CHATGPT_WINDOW_PREFIX = "[ChatRelay]"
TRACKER_WINDOW_PREFIX = "Tracker de messages ChatGPT"
TRACKER_API_URL = "http://localhost:3001/set-message"

# Utility functions

def looking_for_window(window_prefix):
    """
    Search for a window with a specific prefix in its title.

    Args:
        window_prefix (str): The prefix to look for in window titles.

    Returns:
        str or None: The title of the matching window, or None if not found.
    """
    windows = gw.getAllTitles()
    for title in windows:
        if window_prefix in title:
            return title
    return None

def activate_window(target_title):
    """
    Activate a window by its title.

    Args:
        target_title (str): The title of the window to activate.

    Returns:
        bool: True if the window was activated, False otherwise.
    """
    try:
        win = gw.getWindowsWithTitle(target_title)[0]
        win.activate()
        return True
    except IndexError:
        return False

# Refactored functions

def send_text_to_chatgpt(text, status_callback=None, root=None):
    """
    Copy text to clipboard and send it to ChatGPT after a countdown.

    Args:
        text (str): The text to send.
        status_callback (callable, optional): Callback for status updates.
        root (Tk, optional): Root UI element for updates.

    Returns:
        bool: True if the operation started successfully, None otherwise.
    """
    try:
        # pyperclip.copy(text)
        # time.sleep(0.05)
        # Suppression ici — on copiera plus tard dans send_to_chatgpt()

        def countdown_callback(msg):
            if status_callback:
                status_callback(msg, True)

        def after_countdown():
            send_to_chatgpt(root)
            if status_callback:
                status_callback("Texte envoyé à ChatGPT", True)

        def countdown_then_send():
            run_countdown(
                config.get('focus_countdown', 5),
                "Attention, vous avez {n} seconde(s) pour vous focus sur ChatGPT...",
                countdown_callback
            )
            after_countdown()

        threading.Thread(target=countdown_then_send, daemon=True).start()
        return True
    except Exception as e:
        if status_callback:
            status_callback(f"Erreur ChatGPT : {e}", False)
        return None

def send_to_chatgpt(root=None):
    """
    Send text to ChatGPT and optionally update the UI.
    """
    print("[ClipRelay] clique sur send to chatgpt...")

    message = pyperclip.paste()
    if hasattr(root, "text_area"):
        message = root.text_area.get("1.0", "end-1c").strip()

    if message:
        pyperclip.copy(message)
    else:
        print("[ClipRelay] Aucun message trouvé dans text_area pour envoyer.")
        if root and hasattr(root, "status_label"):
            root.status_label.config(text="Rien à envoyer à ChatGPT", fg="red")
        return

    to_gpt(root)
    time.sleep(config['timeouts'].get('after_paste_delay', 1.0))
    to_tracker(root)

def to_gpt(root=None):
    """
    Send text to the ChatGPT window.

    Args:
        root (Tk, optional): Root UI element for updates.
    """
    target_title = looking_for_window(CHATGPT_WINDOW_PREFIX)
    if target_title and activate_window(target_title):
        time.sleep(config['timeouts'].get('window_switch', 0.5))
        pyautogui.hotkey('ctrl', 'v')
        print("[ClipRelay] Texte collé dans la fenêtre [ChatRelay]")
        pyautogui.press('enter')
        if root and hasattr(root, "status_label"):
            root.status_label.config(text="Texte collé et envoyé dans la fenêtre [ChatRelay]", fg="green")
    else:
        print("[ClipRelay] Aucune fenêtre [ChatRelay] trouvée.")
        if root and hasattr(root, "status_label"):
            root.status_label.config(text="Aucune fenêtre [ChatRelay] trouvée.", fg="red")

def to_tracker(root=None):
    """
    Send text to the Tracker window via API.

    Args:
        root (Tk, optional): Root UI element for updates.
    """
    target_title = looking_for_window(TRACKER_WINDOW_PREFIX)
    if target_title and activate_window(target_title):
        print(f"[ClipRelay] Fenêtre trouvée et activée : {target_title}")
        message = pyperclip.paste()
        status_ok = send_to_tracker_via_api(message)
        if root and hasattr(root, "status_label"):
            root.status_label.config(
                text="Texte envoyé au tracker via API", fg="green"
            )
        if status_ok:
            time.sleep(config['timeouts'].get('after_paste_delay', 1.0))
            pyautogui.press('enter')
            print("[ClipRelay] Entrée simulée dans Tracker")
    else:
        print("[ClipRelay] Aucune fenêtre Tracker de messages ChatGPT trouvée.")
        if root and hasattr(root, "status_label"):
            root.status_label.config(
                text="Aucune fenêtre Tracker de messages ChatGPT trouvée.", fg="red"
            )

def send_to_tracker_via_api(message):
    """
    Send a message to the Tracker API.

    Args:
        message (str): The message to send.

    Returns:
        bool: True if the API response is OK, False otherwise.
    """
    try:
        response = requests.post(
            TRACKER_API_URL,
            json={'message': message}
        )
        print("Réponse Electron :", response.json())
        return response.json().get("status") == "ok"
    except Exception as e:
        print("Erreur lors de l'envoi au tracker :", e)
        return False
    
def handle_send_chatgpt(text, status_callback=None):
    """
    Handle sending text to ChatGPT.

    Args:
        text (str): The text to send to ChatGPT.
        status_callback (callable, optional): Callback for status updates.

    Returns:
        None
    """
    send_text_to_chatgpt(
        text,
        status_callback=status_callback
    )

def formater_fichiers_pour_chatgpt(fichiers):
    blocs = []
    for chemin in fichiers:
        try:
            with open(chemin, "r", encoding="utf-8") as f:
                contenu = f.read()
            bloc = f"=== Fichier : {chemin.split('/')[-1]} ===\n{contenu}"
            blocs.append(bloc)
        except Exception as e:
            blocs.append(f"=== Fichier : {chemin.split('/')[-1]} ===\n[Erreur de lecture : {e}]")
    return "\n\n".join(blocs)

def ajouter_fichiers_a_zone_texte(zone_texte):
    contenu_actuel = zone_texte.get("1.0", tk.END).strip()
    if not contenu_actuel:
        print("⚠️ Aucune consigne présente. Ajoutez une consigne avant de joindre des fichiers.")
        return

    fichiers = filedialog.askopenfilenames(title="Choisir les fichiers à joindre")
    if not fichiers:
        return

    contenu_fichiers = formater_fichiers_pour_chatgpt(fichiers)
    zone_texte.insert(tk.END, "\n\n" + contenu_fichiers + "\n")
