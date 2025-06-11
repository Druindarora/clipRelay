import whisper
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write
import threading
import os

MODELE = "small"  # tiny, base, small, medium, large
whisper_model = None  # modèle global

class AudioRecorder:
    def __init__(self, fs=44100, channels=1):
        self.fs = fs
        self.channels = channels
        self.audio = None
        self.recording = False
        self.thread = None

    def start(self, duree_sec=60):
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

def load_whisper_model():
    global whisper_model
    if whisper_model is None:
        print("🧠 Chargement du modèle Whisper...")
        whisper_model = whisper.load_model(MODELE)
        print("✅ Modèle Whisper chargé")
    return whisper_model

def transcrire_audio(fichier_audio):
    if not os.path.exists(fichier_audio):
        print(f"Fichier audio non trouvé : {fichier_audio}")
        return ""
    try:
        model = load_whisper_model()
        print(f"🔍 Transcription en cours... de {fichier_audio}")
        result = model.transcribe(fichier_audio, language="fr")
        texte = result["text"]
        print("📄 Résultat :", texte)
        return texte
    except Exception as e:
        print(f"Erreur lors de la transcription : {e}")
        return ""

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