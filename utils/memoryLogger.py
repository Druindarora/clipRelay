import os
import psutil
import time

from classes.whisper import WHISPER

_timers = {}

def log_memory(tag=""):
    """
    Affiche dans la console la mémoire utilisée par le processus principal.
    """
    process = psutil.Process(os.getpid())
    mem = process.memory_info().rss / (1024 * 1024)  # En MB
    print(f"[MemoryLog] {tag} : {mem:.2f} MB utilisés")

def start_timer(label="default"):
    _timers[label] = {
        "start": time.perf_counter(),
        "mem_start": _get_memory()
    }
    print(f"[Timer] ⏱️ Start '{label}' - Mémoire : {_timers[label]['mem_start']:.2f} MB")

def end_timer(label="default"):
    if label not in _timers:
        print(f"[Timer] ❌ Aucun timer actif avec le label '{label}'")
        return

    end = time.perf_counter()
    mem_end = _get_memory()
    elapsed = end - _timers[label]["start"]
    mem_start = _timers[label]["mem_start"]
    delta_mem = mem_end - mem_start

    print(f"[Timer] ✅ End '{label}' - Durée : {elapsed:.3f} sec | Mémoire : {mem_end:.2f} MB (Δ {delta_mem:+.2f} MB)")
    del _timers[label]

def _get_memory():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)  # En MB

def warmup_model():
    import tempfile
    import numpy as np
    from scipy.io.wavfile import write
    import os

    rate = 16000
    silence = np.zeros(rate, dtype=np.int16)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
        temp_path = temp_file.name

    write(temp_path, rate, silence)

    try:
        WHISPER.transcribe(temp_path)
        print("[Whisper] 🔥 Warmup terminé")
    except Exception as e:
        print(f"[Whisper] ❌ Warmup échoué : {e}")
    finally:
        try:
            os.remove(temp_path)
        except Exception as e:
            print(f"[Whisper] ❌ Impossible de supprimer le fichier temporaire : {e}")

