import time
import tkinter as tk
import threading
import os
import pygetwindow as gw
import keyboard
import pyperclip
from config import config
from services.audioService import AudioRecorder, transcrire_audio, prepare_new_recording, load_whisper_model
from services.chatgptService import send_text_to_chatgpt
from services.vsCodeService import focus_and_paste_in_vscode

def create_popup():
    root = tk.Tk()
    root.title("ClipRelay")
    # Utilise la taille de fenêtre depuis le config
    width, height = config['window_size']
    root.geometry(f"{width}x{height}")

    text_area = tk.Text(root, wrap=tk.WORD)
    text_area.pack(expand=True, fill=tk.BOTH, padx=10, pady=(20, 10))
    root.text_area = text_area

    recorder = AudioRecorder()
    audio_state = {"recording": False, "file_exists": False}

    def handle_record():
        if not audio_state["recording"]:
            # Supprimer l'ancien fichier si présent
            if os.path.exists("enregistrement.wav"):
                os.remove("enregistrement.wav")
            # Effacer la zone de texte
            root.text_area.delete("1.0", tk.END)
            record_btn.config(state=tk.DISABLED)  # Désactive le bouton pendant la transcription
            copy_prefix_btn.config(state=tk.DISABLED)
            send_chatgpt_btn.config(state=tk.DISABLED)
            show_vscode_btn.config(state=tk.DISABLED)
            recorder.start()
            record_btn.config(text="⏹️ Arrêter l'enregistrement")
            root.status_label.config(text="🔴 Enregistrement en cours...", fg="blue")
            print("[ClipRelay] Enregistrement démarré")
            audio_state["recording"] = True
        else:
            fichier = recorder.stop()
            print("[ClipRelay] Arrêt de l'enregistrement demandé")
            if fichier:
                print("[ClipRelay] Enregistrement terminé, lancement de la transcription")
                root.status_label.config(text="🔄 Transcription en cours...", fg="blue")
                audio_state["file_exists"] = True
                # Désactive le bouton pendant la transcription
                record_btn.config(state=tk.DISABLED)
                threading.Thread(target=handle_transcribe).start()
            else:
                root.status_label.config(text="❌ Erreur lors de l'arrêt.", fg="red")
                print("[ClipRelay] Erreur lors de l'arrêt de l'enregistrement")
                # Réactive tous les boutons même en cas d'erreur
                record_btn.config(state=tk.NORMAL)
                copy_prefix_btn.config(state=tk.NORMAL)
                send_chatgpt_btn.config(state=tk.NORMAL)
                show_vscode_btn.config(state=tk.NORMAL)
            record_btn.config(text="🎙️ Démarrer l'enregistrement")
            audio_state["recording"] = False

    def handle_transcribe():
        try:
            print("[ClipRelay] Début transcription")
            if not os.path.exists("enregistrement.wav"):
                root.status_label.config(text="❌ Fichier audio non trouvé.", fg="red")
                print("[ClipRelay] Fichier audio non trouvé pour la transcription")
                # Réactive les boutons même en cas d'échec
                record_btn.config(state=tk.NORMAL)
                copy_prefix_btn.config(state=tk.NORMAL)
                send_chatgpt_btn.config(state=tk.NORMAL)
                show_vscode_btn.config(state=tk.NORMAL)
                return
            texte = transcrire_audio("enregistrement.wav")
            root.text_area.delete("1.0", tk.END)
            root.text_area.insert(tk.END, texte)
            root.status_label.config(text="✅ Transcription terminée.", fg="green")
            print("[ClipRelay] Transcription terminée")
            # Réactive les boutons seulement ici
            record_btn.config(state=tk.NORMAL)
            copy_prefix_btn.config(state=tk.NORMAL)
            send_chatgpt_btn.config(state=tk.NORMAL)
            show_vscode_btn.config(state=tk.NORMAL)
        except Exception as e:
            root.status_label.config(text=f"Erreur transcription: {e}", fg="red")
            print(f"[ClipRelay] Erreur transcription: {e}")
            # Réactive les boutons même en cas d'erreur
            record_btn.config(state=tk.NORMAL)
            copy_prefix_btn.config(state=tk.NORMAL)
            send_chatgpt_btn.config(state=tk.NORMAL)
            show_vscode_btn.config(state=tk.NORMAL)

    record_btn = tk.Button(root, text="Démarrer l'enregistrement", command=handle_record)
    record_btn.pack(pady=(0, 10))

    button_frame = tk.Frame(root)
    button_frame.pack(pady=10)

    col_offset = 0

    copy_prefix_btn = tk.Button(button_frame, text="📋 Copier [ChatRelay]", command=lambda: copy_chatrelay_prefix())
    copy_prefix_btn.grid(row=0, column=0 + col_offset, padx=10)

    def handle_send_chatgpt():
        text = root.text_area.get("1.0", "end-1c")
        send_text_to_chatgpt(
            text,
            status_callback=lambda msg, ok: root.status_label.config(text=msg, fg="green" if ok else "red")
        )

    send_chatgpt_btn = tk.Button(button_frame, text="Envoyer vers ChatGPT", command=handle_send_chatgpt)
    send_chatgpt_btn.grid(row=0, column=1 + col_offset, padx=10)

    show_vscode_btn = tk.Button(
        button_frame,
        text="Focus VS Code",
        command=lambda: focus_vscode(root)
    )
    show_vscode_btn.grid(row=0, column=2 + col_offset, padx=10)

    # La zone de message Succès/Erreur passe ici
    status_label = tk.Label(root, text="", fg="red")
    status_label.pack(pady=(10, 5))
    root.status_label = status_label

    # La zone de compte à rebours reste en bas
    countdown_label = tk.Label(root, text="", fg="red")
    countdown_label.pack(pady=(0, 20))
    root.countdown_label = countdown_label

    # Charger Whisper au démarrage
    threading.Thread(target=load_whisper_model).start()

    return root

def copy_chatrelay_prefix():
    pyperclip.copy("[ChatRelay] ")
    print("[ClipRelay] Préfixe [ChatRelay] copié dans le presse-papiers")

def log_status(root, message, success=False):
    print(f"[ClipRelay] {message}")
    if root and hasattr(root, "status_label"):
        color = "green" if success else "red"
        root.status_label.config(text=message, fg=color)

def on_hotkey(event=None, root=None):
    try:
        if root:
            root.withdraw()
            # Utilise le délai configurable
            time.sleep(config['timeouts']['hotkey_delay'])
        keyboard.send('ctrl+a')
        time.sleep(config['timeouts']['text_input'])
        keyboard.send('ctrl+x')
        time.sleep(config['timeouts']['text_input'])
        text = pyperclip.paste()
        log_status(root, f"Texte coupé ({len(text)} caractères) : '{text[:50]}'", success=True)
        if root:
            root.deiconify()
            root.lift()
            root.focus_force()
            root.text_area.delete("1.0", tk.END)
            root.text_area.insert(tk.END, text)
    except Exception as e:
        log_status(root, f"Erreur : {e}")

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

prepare_new_recording("enregistrement.wav")
