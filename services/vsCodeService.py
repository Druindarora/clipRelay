import pygetwindow as gw
import keyboard
import time
import pyperclip
import threading

def focus_and_paste_in_vscode(text, config, status_callback=None, countdown_callback=None):
    def countdown_and_focus():
        pyperclip.copy(text)
        time.sleep(0.05)
        windows = gw.getWindowsWithTitle("Visual Studio Code")
        if windows:
            win = windows[0]
            win.activate()
            time.sleep(config['timeouts']['window_switch'])
            for i in range(5, 0, -1):
                if countdown_callback:
                    countdown_callback(f"Attention, vous avez 5 secondes pour vous focus sur le chat : {i}")
                time.sleep(1)
            if countdown_callback:
                countdown_callback("")
            active_title = get_active_window_title()
            if active_title and "Visual Studio Code" in active_title:
                keyboard.send('ctrl+v')
                time.sleep(config['timeouts']['paste_delay'])
                keyboard.send('enter')
                if status_callback:
                    status_callback("Texte collé et envoyé dans VS Code", True)
            else:
                if status_callback:
                    status_callback("Le focus n'est pas sur VS Code !", False)
        else:
            if status_callback:
                status_callback("VS Code non trouvé", False)

    threading.Thread(target=countdown_and_focus).start()

def get_active_window_title():
    win = gw.getActiveWindow()
    if win:
        return win.title
    return None
