import time
import re
import os
import threading
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
import tkinter as tk
from tkinter import messagebox

from config import MAGIC_PHRASES
from utils.userSettings import load_user_settings
from utils.textProcessing import nettoyer_texte_transcription
from classes.whisper import WHISPER  # 🧠 L'objet orienté

class AudioRecorder:
    def __init__(self, fs=44100, channels=1):
        self.fs = fs
        self.channels = channels
        self.audio = None
        self.recording = False
        self.thread = None

    def start(self, duree_sec=None):
        if duree_sec is None:
            settings = load_user_settings()
            duree_sec = settings.get("duree_enregistrement", 60)
        self.audio = np.empty((0, self.channels), dtype=np.float32)
        self.recording = True
        self.thread = threading.Thread(target=self._record, args=(duree_sec,))
        self.thread.start()

    def _record(self, duree_sec):
        self.audio = sd.rec(int(duree_sec * self.fs), samplerate=self.fs, channels=self.channels)
        sd.wait()
        self.recording = False

    def stop(self, fichier="enregistrement.wav"):
        if self.audio is not None:
            audio_int16 = np.int16(self.audio / np.max(np.abs(self.audio)) * 32767)
            write(fichier, self.fs, audio_int16)
            return fichier
        return None

def transcrire_audio(fichier_audio, boutons_a_geler, root):
    if not os.path.exists(fichier_audio):
        print(f"[ClipRelay] Fichier audio non trouvé : {fichier_audio}")
        return ""
    try:
        for btn in boutons_a_geler:
            if btn:
                btn.config(state="disabled")

        print(f"[ClipRelay] Transcription en cours... de {fichier_audio}")
        start_time = time.time()
        texte = WHISPER.transcribe(fichier_audio)

        mots = texte.split()
        texte_final = []

        for mot in mots:
            mot_nettoye = re.sub(r"[^\w]", "", mot).lower()
            texte_final.append(mot)
            if mot_nettoye in [m.lower() for m in MAGIC_PHRASES]:
                print(f"[ClipRelay] Mot magique détecté ('{mot}'), arrêt après ce mot.")
                break

        texte_final = " ".join(texte_final)

        end_time = time.time()
        duration = end_time - start_time
        if hasattr(root, "transcription_time_var"):
            root.transcription_time_var.set(f"Temps de transcription : {duration:.2f} secondes")

        return texte_final
    except Exception as e:
        print(f"[ClipRelay] Erreur lors de la transcription : {e}")
        return ""
    finally:
        for btn in boutons_a_geler:
            if btn:
                btn.config(state="normal")

def handle_transcribe(root, state_manager, record_btn, copy_prefix_btn, send_chatgpt_btn, show_vscode_btn, copy_pollution_btn):
    try:
        print("[ClipRelay] Début transcription")
        if not os.path.exists("enregistrement.wav"):
            state_manager.update_status("Fichier audio non trouvé.", "red")
            state_manager.set_buttons_state("normal")
            return

        start_time = time.time()
        texte = transcrire_audio("enregistrement.wav", [record_btn, copy_prefix_btn, send_chatgpt_btn, show_vscode_btn, copy_pollution_btn], root)
        end_time = time.time()

        texte = nettoyer_texte_transcription(texte)
        root.text_area.delete("1.0", tk.END)
        root.text_area.insert(tk.END, texte)
        state_manager.update_status("Transcription terminée.", "green")
        print("[ClipRelay] Transcription terminée")

        if hasattr(root, "transcription_time_var"):
            root.transcription_time_var.set(f"Temps de transcription : {end_time - start_time:.2f} secondes")

        state_manager.set_buttons_state("normal")

        if MAGIC_PHRASES[0] in texte:
            print(f"[ClipRelay] Mot magique détecté ('{MAGIC_PHRASES[0]}')")
    except Exception as e:
        state_manager.update_status(f"Erreur transcription: {e}", "red")
        print(f"[ClipRelay] Erreur transcription: {e}")
        state_manager.set_buttons_state("normal")

def handle_record(root, recorder, audio_state, state_manager, copy_prefix_btn, send_chatgpt_btn, show_vscode_btn, record_btn=None, copy_pollution_btn=None):
    def update_timer():
        if audio_state["recording"]:
            elapsed = int(time.time() - audio_state["start_time"])
            minutes = elapsed // 60
            seconds = elapsed % 60
            root.timer_var.set(f"{minutes:02d}:{seconds:02d}")
            root.after(1000, update_timer)

    try:
        if not audio_state["recording"]:
            if os.path.exists("enregistrement.wav"):
                os.remove("enregistrement.wav")
            root.text_area.delete("1.0", tk.END)
            state_manager.set_buttons_state("disabled")

            recorder.start()
            root.timer_var.set("00:00")
            root.transcription_time_var.set("Temps de transcription : --")

            record_btn.config(text="Arrêter l'enregistrement", image=root.img_stop_record)
            record_btn.image = root.img_stop_record
            state_manager.update_status("Enregistrement en cours...", "orange")

            print("[ClipRelay] Enregistrement démarré")
            audio_state["recording"] = True
            audio_state["start_time"] = time.time()
            update_timer()
        else:
            fichier = recorder.stop()
            print("[ClipRelay] Arrêt de l'enregistrement demandé")

            if fichier:
                print("[ClipRelay] Enregistrement terminé, lancement transcription")
                state_manager.update_status("Transcription en cours...", "orange")
                audio_state["file_exists"] = True
                record_btn.config(state=tk.DISABLED)
                threading.Thread(target=handle_transcribe, args=(
                    root, state_manager, record_btn, copy_prefix_btn, send_chatgpt_btn, show_vscode_btn, copy_pollution_btn)).start()
            else:
                state_manager.update_status("Erreur lors de l'arrêt.", "red")
                state_manager.set_buttons_state("normal")
            record_btn.config(text="Démarrer l'enregistrement", image=root.img_start_record)
            record_btn.image = root.img_start_record
            audio_state["recording"] = False
            state_manager.set_buttons_state("normal")
    except Exception as e:
        state_manager.update_status(f"Erreur lors de l'enregistrement: {e}", "red")
        print(f"[ClipRelay] Erreur lors de l'enregistrement: {e}")
        state_manager.set_buttons_state("normal")
