import keyboard
from ui.mainWindow import create_popup
from ui.shortcuts import on_hotkey
from services import podcastService

if __name__ == "__main__":
    root = create_popup()
    keyboard.add_hotkey('ctrl+shift+f12', lambda: on_hotkey(root=root))
    print("DEBUG: raccourci clavier attaché")
    root.mainloop()

def on_close():
    if podcastService.server_running:
        print("[ClipRelay] Fermeture de l'application : arrêt du serveur podcast...")
        # On laisse le thread se terminer
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)
