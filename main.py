import keyboard
from ui.mainWindow import create_popup
from ui.shortcuts import on_hotkey

if __name__ == "__main__":
    root = create_popup()
    keyboard.add_hotkey('ctrl+shift+f12', lambda: on_hotkey(root=root))
    print("⏳ En attente du raccourci clavier CTRL + MAJ + F12...")
    root.mainloop()