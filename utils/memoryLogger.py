import os
import psutil

def log_memory(tag=""):
    """
    Affiche dans la console la mémoire utilisée par le processus principal.
    """
    process = psutil.Process(os.getpid())
    mem = process.memory_info().rss / (1024 * 1024)  # En MB
    print(f"[MemoryLog] {tag} : {mem:.2f} MB utilisés")
