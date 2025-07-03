import keyboard
from ui.mainWindow import create_popup
from ui.shortcuts import on_hotkey
from services import podcastService
from utils.memoryLogger import log_memory

if __name__ == "__main__":
    root = create_popup()

    def on_close():
        try:
            if podcastService.is_port_in_use(podcastService.PORT):
                print("[ClipRelay] Fermeture de l'application : arrêt du serveur podcast...")
            else:
                print("[ClipRelay] Fermeture de l'application : aucun serveur podcast détecté.")
        except Exception as e:
            print(f"[ClipRelay] Erreur pendant la fermeture : {e}")
        finally:
            root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)

    log_memory("App démarrée")
    keyboard.add_hotkey('ctrl+shift+f12', lambda: on_hotkey(root=root))
    print("DEBUG: raccourci clavier attaché")
    root.mainloop()
