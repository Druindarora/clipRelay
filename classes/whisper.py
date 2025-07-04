# 📁 classes/whisper.py

import torch
import whisper

class Whisper:
    def __init__(self):
        self._model = None
        self._model_name = None
        self._device = "cuda" if torch.cuda.is_available() else "cpu"

    @property
    def is_ready(self):
        return self._model is not None

    def load(self, model_name):
        if self._model_name == model_name and self.is_ready:
            return
        print(f"[Whisper] Chargement du modèle '{model_name}' sur {self._device}")
        self._model = whisper.load_model(model_name).to(self._device)
        self._model_name = model_name
        print("[Whisper] ✅ Modèle prêt")

    def unload(self):
        self._model = None
        self._model_name = None
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        print("[Whisper] 🔄 Modèle déchargé")

    def transcribe(self, audio_path):
        if not self.is_ready:
            raise RuntimeError("Le modèle n'est pas chargé")
        print(f"[Whisper] Transcription de '{audio_path}'...")
        result = self._model.transcribe(audio_path, language="fr")
        return result.get("text", "")

    @property
    def model_name(self):
        return self._model_name or "(aucun)"

# 👇 Singleton utilisable dans tout le projet
WHISPER = Whisper()
