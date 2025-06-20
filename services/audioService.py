import time
from tkinter import messagebox
import whisper
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import threading
import os
import tkinter as tk

from utils.userSettings import PHRASES_A_SUPPRIMER_PAR_DEFAUT, load_user_settings, save_user_settings

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

def load_whisper_model(modele=None):
    global whisper_model, MODELE
    if modele:
        MODELE = modele
        whisper_model = None  # Force le rechargement
    if whisper_model is None:
        print(f"Chargement du modèle Whisper ({MODELE})...")
        whisper_model = whisper.load_model(MODELE)
        print(f"Modèle Whisper chargé : {MODELE}")  # <-- Log du modèle chargé
    else:
        print(f"Modèle Whisper déjà chargé : {MODELE}")  # <-- Log si déjà chargé
    return whisper_model

def transcrire_audio(fichier_audio, boutons_a_geler):
    if not os.path.exists(fichier_audio):
        print(f"Fichier audio non trouvé : {fichier_audio}")
        return ""
    try:
        # Désactiver tous les boutons
        for btn in boutons_a_geler:
            if btn:
                btn.config(state="disabled")

        model = load_whisper_model()
        print(f"Transcription en cours... de {fichier_audio}")
        result = model.transcribe(fichier_audio, language="fr")
        texte = result["text"]
        print("Résultat :", texte)
        return texte
    except Exception as e:
        print(f"Erreur lors de la transcription : {e}")
        return ""
    finally:
        # Réactiver tous les boutons même en cas d'erreur
        for btn in boutons_a_geler:
            if btn:
                btn.config(state="normal")

def prepare_new_recording(fichier="enregistrement.wav"):
    """Supprime l'ancien fichier d'enregistrement s'il existe."""
    if os.path.exists(fichier):
        os.remove(fichier)

if __name__ == "__main__":
    wav_file = "enregistrement.wav"
    prepare_new_recording(wav_file)
    recorder = AudioRecorder()
    recorder.start(5)
    recorder.thread.join()  # Attendre la fin de l'enregistrement
    fichier_audio = recorder.stop(wav_file)
    transcrire_audio(fichier_audio)

def handle_record(root, recorder, audio_state, copy_prefix_btn, send_chatgpt_btn, show_vscode_btn, record_btn=None, copy_pollution_btn=None):
    def update_timer():
        if audio_state["recording"]:
            elapsed = int(time.time() - audio_state["start_time"])
            minutes = elapsed // 60
            seconds = elapsed % 60
            root.timer_var.set(f"{minutes:02d}:{seconds:02d}")
            root.after(1000, update_timer)

    if not audio_state["recording"]:
        if os.path.exists("enregistrement.wav"):
            os.remove("enregistrement.wav")
        root.text_area.delete("1.0", tk.END)
        # Désactiver tous les boutons SAUF record_btn pendant l'enregistrement
        for btn in [copy_prefix_btn, send_chatgpt_btn, show_vscode_btn, copy_pollution_btn]:
            if btn:
                btn.config(state="disabled")
        # record_btn reste actif pour permettre l'arrêt

        recorder.start()
        record_btn.config(
            text="Arrêter l'enregistrement",
            image=root.img_stop_record
        )
        record_btn.image = root.img_stop_record
        root.status_label.config(text="Enregistrement en cours...", fg="blue")
        print("[ClipRelay] Enregistrement démarré")
        audio_state["recording"] = True
        audio_state["start_time"] = time.time()
        root.timer_var.set("00:00")  # Remise à zéro UNIQUEMENT au démarrage
        update_timer()
    else:
        fichier = recorder.stop()
        print("[ClipRelay] Arrêt de l'enregistrement demandé")
        if fichier:
            print("[ClipRelay] Enregistrement terminé, lancement de la transcription")
            root.status_label.config(text="Transcription en cours...", fg="blue")
            audio_state["file_exists"] = True
            record_btn.config(state=tk.DISABLED)
            threading.Thread(target=handle_transcribe, args=(root, record_btn, copy_prefix_btn, send_chatgpt_btn, show_vscode_btn, copy_pollution_btn)).start()
        else:
            root.status_label.config(text="Erreur lors de l'arrêt.", fg="red")
            print("[ClipRelay] Erreur lors de l'arrêt de l'enregistrement")
            record_btn.config(state=tk.NORMAL)
            copy_prefix_btn.config(state=tk.NORMAL)
            send_chatgpt_btn.config(state=tk.NORMAL)
            show_vscode_btn.config(state=tk.NORMAL)
        record_btn.config(
            text="Démarrer l'enregistrement",
            image=root.img_start_record
        )
        record_btn.image = root.img_start_record
        audio_state["recording"] = False
        # Réactiver tous les boutons à la fin
        for btn in [copy_prefix_btn, send_chatgpt_btn, show_vscode_btn, record_btn, copy_pollution_btn]:
            if btn:
                btn.config(state="normal")

def nettoyer_texte_transcription(texte):
    """Supprime les phrases polluantes du texte de transcription."""
    for phrase in PHRASES_A_SUPPRIMER_PAR_DEFAUT:
        texte = texte.replace(phrase, "")
    # Optionnel : supprime les lignes vides créées
    texte = "\n".join([line for line in texte.splitlines() if line.strip() != ""])
    return texte

def handle_transcribe(root, record_btn, copy_prefix_btn, send_chatgpt_btn, show_vscode_btn, copy_pollution_btn):
    try:
        print("[ClipRelay] Début transcription")
        if not os.path.exists("enregistrement.wav"):
            root.status_label.config(text="Fichier audio non trouvé.", fg="red")
            print("[ClipRelay] Fichier audio non trouvé pour la transcription")
            record_btn.config(state=tk.NORMAL)
            copy_prefix_btn.config(state=tk.NORMAL)
            send_chatgpt_btn.config(state=tk.NORMAL)
            show_vscode_btn.config(state=tk.NORMAL)
            return
        texte = transcrire_audio("enregistrement.wav", [record_btn, copy_prefix_btn, send_chatgpt_btn, show_vscode_btn, copy_pollution_btn])
        texte = nettoyer_texte_transcription(texte)  # <-- Nettoyage ici
        root.text_area.delete("1.0", tk.END)
        root.text_area.insert(tk.END, texte)
        root.status_label.config(text="Transcription terminée.", fg="green")
        print("[ClipRelay] Transcription terminée")
        record_btn.config(state=tk.NORMAL)
        copy_prefix_btn.config(state=tk.NORMAL)
        send_chatgpt_btn.config(state=tk.NORMAL)
        show_vscode_btn.config(state=tk.NORMAL)
    except Exception as e:
        root.status_label.config(text=f"Erreur transcription: {e}", fg="red")
        print(f"[ClipRelay] Erreur transcription: {e}")
        record_btn.config(state=tk.NORMAL)
        copy_prefix_btn.config(state=tk.NORMAL)
        send_chatgpt_btn.config(state=tk.NORMAL)
        show_vscode_btn.config(state=tk.NORMAL)

def changer_modele_whisper(modele, root, record_btn, copy_prefix_btn, send_chatgpt_btn, show_vscode_btn):
    import services.audioService
    modele_court = modele.split("-")[-1]  # Exemple pour extraire la partie après le tiret
    for widget in [record_btn, copy_prefix_btn, send_chatgpt_btn, show_vscode_btn]:
        widget.config(state=tk.DISABLED)
    root.status_label.config(text=f"Chargement du modèle {modele_court}...", fg="blue")
    print(f"[ClipRelay] Chargement du modèle {modele_court}")
    def load_and_reenable():
        services.audioService.load_whisper_model(modele)
        root.status_label.config(text=f"Modèle {modele_court} chargé !", fg="green")
        root.modele_var.set(f"Modèle : {modele_court}")
        print(f"[ClipRelay] Modèle Whisper chargé : {modele_court}")
        # Sauvegarde du modèle choisi
        settings = load_user_settings()
        settings["modele"] = modele
        save_user_settings(settings)
        for widget in [record_btn, copy_prefix_btn, send_chatgpt_btn, show_vscode_btn]:
            widget.config(state=tk.NORMAL)
    threading.Thread(target=load_and_reenable).start()