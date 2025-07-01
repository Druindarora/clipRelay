import time
from tkinter import messagebox
import torch
import whisper
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import threading
import os
import tkinter as tk
from utils.userSettings import PHRASES_A_SUPPRIMER_PAR_DEFAUT, load_user_settings, save_user_settings
from utils.textProcessing import nettoyer_texte_transcription  # Importation ici pour éviter les imports circulaires

MAGIC_WORDS = ["Orpax", "orpax", "Or pax", "Or Pax", "orp axe", "Horpax", "horpax"]  # Liste des variantes du mot magique

class AudioRecorder:
    """
    A class to handle audio recording using sounddevice.

    Attributes:
        fs (int): Sampling frequency.
        channels (int): Number of audio channels.
        audio (numpy.ndarray): Recorded audio data.
        recording (bool): Flag indicating if recording is active.
        thread (threading.Thread): Thread handling the recording process.
    """

    def __init__(self, fs=44100, channels=1):
        """
        Initialize the AudioRecorder.

        Args:
            fs (int): Sampling frequency. Default is 44100.
            channels (int): Number of audio channels. Default is 1.
        """
        self.fs = fs
        self.channels = channels
        self.audio = None
        self.recording = False
        self.thread = None

    def start(self, duree_sec=None):
        """
        Start recording audio.

        Args:
            duree_sec (int, optional): Duration of the recording in seconds. If None, loads from user settings.
        """
        if duree_sec is None:
            settings = load_user_settings()
            duree_sec = settings.get("duree_enregistrement", 60)
        self.audio = np.empty((0, self.channels), dtype=np.float32)
        self.recording = True
        self.thread = threading.Thread(target=self._record, args=(duree_sec,))
        self.thread.start()

    def _record(self, duree_sec):
        """
        Internal method to record audio.

        Args:
            duree_sec (int): Duration of the recording in seconds.
        """
        self.audio = sd.rec(int(duree_sec * self.fs), samplerate=self.fs, channels=self.channels)
        sd.wait()
        self.recording = False

    def stop(self, fichier="enregistrement.wav"):
        """
        Stop recording and save the audio to a file.

        Args:
            fichier (str): Path to save the recorded audio file. Default is "enregistrement.wav".

        Returns:
            str or None: Path to the saved file, or None if no audio was recorded.
        """
        if self.audio is not None:
            audio_int16 = np.int16(self.audio / np.max(np.abs(self.audio)) * 32767)
            write(fichier, self.fs, audio_int16)
            return fichier
        return None

def load_whisper_model(modele=None):
    """
    Load the Whisper model for transcription.

    Args:
        modele (str, optional): Name of the Whisper model to load. If None, uses the default model.

    Returns:
        whisper.Model: Loaded Whisper model.
    """
    global whisper_model, MODELE
    if modele:
        MODELE = modele
        whisper_model = None  # Force le rechargement
    if whisper_model is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        whisper_model = whisper.load_model(MODELE, device=device)
    return whisper_model

def transcrire_audio(fichier_audio, boutons_a_geler):
    """
    Transcribe audio using the Whisper model.

    Args:
        fichier_audio (str): Path to the audio file to transcribe.
        boutons_a_geler (list): List of buttons to disable during transcription.

    Returns:
        str: Transcribed text.
    """
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

        # Démarrage du timer
        start_time = time.time()

        result = model.transcribe(fichier_audio, language="fr")
        texte = result["text"]

        # Vérification des variantes du mot magique et arrêt après celui-ci
        texte_final = []
        for mot in texte.split():
            texte_final.append(mot)
            if mot in MAGIC_WORDS:
                print(f"Mot magique détecté ('{mot}'), arrêt de la transcription après ce mot.")
                break

        texte_final = " ".join(texte_final)

        # Arrêt du timer
        end_time = time.time()
        duration = end_time - start_time
        print(f"Durée de la transcription : {duration:.2f} secondes")

        print("Résultat :", texte_final)
        return texte_final
    except Exception as e:
        print(f"Erreur lors de la transcription : {e}")
        return ""
    finally:
        # Réactiver tous les boutons même en cas d'erreur
        for btn in boutons_a_geler:
            if btn:
                btn.config(state="normal")

def prepare_new_recording(fichier="enregistrement.wav"):
    """
    Supprime l'ancien fichier d'enregistrement s'il existe.

    Args:
        fichier (str): Chemin du fichier d'enregistrement à supprimer. Par défaut "enregistrement.wav".
    """
    if os.path.exists(fichier):
        os.remove(fichier)

def handle_transcribe(root, state_manager, record_btn, copy_prefix_btn, send_chatgpt_btn, show_vscode_btn, copy_pollution_btn):
    """
    Gère la transcription de l'audio enregistré.

    Args:
        root (Tk): La fenêtre principale.
        state_manager (StateManager): Gestionnaire des états des boutons et labels.
        record_btn (Button): Bouton pour démarrer/arrêter l'enregistrement.
        copy_prefix_btn (Button): Bouton pour copier le préfixe.
        send_chatgpt_btn (Button): Bouton pour envoyer à ChatGPT.
        show_vscode_btn (Button): Bouton pour afficher dans VS Code.
        copy_pollution_btn (Button): Bouton pour copier les phrases anti-pollution.

    Returns:
        None
    """
    import os
    import tkinter as tk
    from utils.textProcessing import nettoyer_texte_transcription

    try:
        print("[ClipRelay] Début transcription")
        if not os.path.exists("enregistrement.wav"):
            state_manager.update_status("Fichier audio non trouvé.", "red")
            print("[ClipRelay] Fichier audio non trouvé pour la transcription")
            state_manager.set_buttons_state("normal")
            return
        texte = transcrire_audio("enregistrement.wav", [record_btn, copy_prefix_btn, send_chatgpt_btn, show_vscode_btn, copy_pollution_btn])
        texte = nettoyer_texte_transcription(texte)  # <-- Nettoyage ici
        root.text_area.delete("1.0", tk.END)
        root.text_area.insert(tk.END, texte)
        state_manager.update_status("Transcription terminée.", "green")
        print("[ClipRelay] Transcription terminée")
        state_manager.set_buttons_state("normal")
    except Exception as e:
        state_manager.update_status(f"Erreur transcription: {e}", "red")
        print(f"[ClipRelay] Erreur transcription: {e}")
        state_manager.set_buttons_state("normal")

def handle_record(root, recorder, audio_state, state_manager, copy_prefix_btn, send_chatgpt_btn, show_vscode_btn, record_btn=None, copy_pollution_btn=None):
    """
    Gère l'enregistrement audio et son arrêt.

    Args:
        root (Tk): La fenêtre principale.
        recorder (AudioRecorder): L'objet enregistreur audio.
        audio_state (dict): L'état audio actuel.
        state_manager (StateManager): Gestionnaire des états des boutons et labels.
        copy_prefix_btn (Button): Bouton pour copier le préfixe.
        send_chatgpt_btn (Button): Bouton pour envoyer à ChatGPT.
        show_vscode_btn (Button): Bouton pour afficher dans VS Code.
        record_btn (Button, optional): Bouton pour démarrer/arrêter l'enregistrement.
        copy_pollution_btn (Button, optional): Bouton pour copier les phrases anti-pollution.

    Returns:
        None
    """
    import time
    import os
    import tkinter as tk

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
            record_btn.config(
                text="Arrêter l'enregistrement",
                image=root.img_stop_record
            )
            record_btn.image = root.img_stop_record
            state_manager.update_status("Enregistrement en cours...", "orange")
            print("[ClipRelay] Enregistrement démarré")
            audio_state["recording"] = True
            audio_state["start_time"] = time.time()
            root.timer_var.set("00:00")
            update_timer()
        else:
            fichier = recorder.stop()
            print("[ClipRelay] Arrêt de l'enregistrement demandé")
            if fichier:
                print("[ClipRelay] Enregistrement terminé, lancement de la transcription")
                state_manager.update_status("Transcription en cours...", "orange")
                audio_state["file_exists"] = True
                record_btn.config(state=tk.DISABLED)
                threading.Thread(target=handle_transcribe, args=(root, state_manager, record_btn, copy_prefix_btn, send_chatgpt_btn, show_vscode_btn, copy_pollution_btn)).start()
            else:
                state_manager.update_status("Erreur lors de l'arrêt.", "red")
                print("[ClipRelay] Erreur lors de l'arrêt de l'enregistrement")
                state_manager.set_buttons_state("normal")
            record_btn.config(
                text="Démarrer l'enregistrement",
                image=root.img_start_record
            )
            record_btn.image = root.img_start_record
            audio_state["recording"] = False
            state_manager.set_buttons_state("normal")
    except Exception as e:
        state_manager.update_status(f"Erreur lors de l'enregistrement: {e}", "red")
        print(f"[ClipRelay] Erreur lors de l'enregistrement: {e}")
        state_manager.set_buttons_state("normal")

if __name__ == "__main__":
    wav_file = "enregistrement.wav"
    prepare_new_recording(wav_file)
    recorder = AudioRecorder()
    recorder.start(5)
    recorder.thread.join()  # Attendre la fin de l'enregistrement
    fichier_audio = recorder.stop(wav_file)
    transcrire_audio(fichier_audio)