import gc
import threading
import keyboard
import torch
from ui.mainWindow import create_popup
from ui.shortcuts import on_hotkey
from services import podcastService
from utils.memoryLogger import end_timer, log_memory, start_timer, warmup_model
from utils.userSettings import load_user_settings
from classes.whisper import WHISPER  # 🆕

if __name__ == "__main__":
    root = create_popup()

    def on_close():
        start_timer("on_close")
        try:
            if podcastService.is_port_in_use(podcastService.PORT):
                print("[ClipRelay] Fermeture de l'application : arrêt du serveur podcast...")
            else:
                print("[ClipRelay] Fermeture de l'application : aucun serveur podcast détecté.")
        except Exception as e:
            print(f"[ClipRelay] Erreur pendant la fermeture : {e}")
        finally:
            root.destroy()
        try:
            WHISPER.unload()  # 🧠 Libération mémoire personnalisée
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                print("[ClipRelay] 🔧 GPU cache vidé")
        except Exception as e:
            print(f"[ClipRelay] ⚠️ torch.cuda.empty_cache() a échoué : {e}")

        gc.collect()
        print("[ClipRelay] 🔧 Garbage collector lancé")
        end_timer("on_close")

    root.protocol("WM_DELETE_WINDOW", on_close)

    # ✅ Chargement du modèle au démarrage via l'objet orienté
    settings = load_user_settings()
    modele = settings.get("modele", "base")
    WHISPER.load(modele)
    threading.Thread(target=warmup_model).start()

    log_memory("App démarrée")
    keyboard.add_hotkey('ctrl+shift+f12', lambda: on_hotkey(root=root))
    print("DEBUG: raccourci clavier attaché")
    root.mainloop()
