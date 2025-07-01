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

if __name__ == "__main__":
    wav_file = "enregistrement.wav"
    prepare_new_recording(wav_file)
    recorder = AudioRecorder()
    recorder.start(5)
    recorder.thread.join()  # Attendre la fin de l'enregistrement
    fichier_audio = recorder.stop(wav_file)
    transcrire_audio(fichier_audio)