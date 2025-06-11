import time
import tkinter as tk
import pyautogui
import pygetwindow as gw
import pyperclip
from config import config
import requests

def send_to_chatgpt(root=None):
    print("[ClipRelay] clique sur send to chatgpt...")
    to_gpt(root)
    time.sleep(config['timeouts'].get('after_paste_delay', 1.0))  # Délai pour laisser le temps à ChatGPT de coller
    to_tracker(root)

def to_gpt(root=None):
    target_title = looking_for_window("[ChatRelay]")
    if target_title:
        win = gw.getWindowsWithTitle(target_title)[0]
        win.activate()
        time.sleep(0.2)
        print(f"[ClipRelay] Fenêtre trouvée et activée : {target_title}")
        pyautogui.hotkey('ctrl', 'v')
        print("[ClipRelay] Texte collé dans la fenêtre [ChatRelay]")
        # Allonge le délai avant d'appuyer sur Entrée
        time.sleep(config['timeouts'].get('after_paste_delay', 1.0))  # Par défaut 1s si non défini
        pyautogui.press('enter')
        print("[ClipRelay] Entrée simulée dans [ChatRelay]")
        if root and hasattr(root, "status_label"):
            root.status_label.config(text="Texte collé et envoyé dans la fenêtre [ChatRelay]", fg="green")
    else:
        print("[ClipRelay] Aucune fenêtre [ChatRelay] trouvée.")
        if root and hasattr(root, "status_label"):
            root.status_label.config(text="Aucune fenêtre [ChatRelay] trouvée.", fg="red")

def to_tracker(root=None):
    target_title = looking_for_window("Tracker de messages ChatGPT")
    if target_title:
        win = gw.getWindowsWithTitle(target_title)[0]
        win.activate()
        print(f"[ClipRelay] Fenêtre trouvée et activée : {target_title}")
        message = pyperclip.paste()
        status_ok = send_to_tracker_via_api(message)
        if root and hasattr(root, "status_label"):
            root.status_label.config(
                text="Texte envoyé au tracker via API", fg="green"
            )
        # Si la réponse Electron est ok, on attend puis on simule Entrée
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

def looking_for_window(window_prefix):
    windows = gw.getAllTitles()
    for title in windows:
        if title.startswith(window_prefix):
            return title
    return None

def send_to_tracker_via_api(message):
    try:
        response = requests.post(
            'http://localhost:3001/set-message',
            json={'message': message}
        )
        print("Réponse Electron :", response.json())
        # Retourne True si status ok, sinon False
        return response.json().get("status") == "ok"
    except Exception as e:
        print("Erreur lors de l'envoi au tracker :", e)
        return False

def send_text_to_chatgpt(text, status_callback=None, root=None):
    try:
        pyperclip.copy(text)
        time.sleep(0.05)
        send_to_chatgpt(root)
        if status_callback:
            status_callback("Texte envoyé à ChatGPT", True)
        return True
    except Exception as e:
        if status_callback:
            status_callback(f"Erreur ChatGPT : {e}", False)
        return None