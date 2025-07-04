import tkinter as tk
from utils.memoryLogger import end_timer, log_memory, start_timer
from utils.userSettings import load_user_settings, save_user_settings
from ui.menuBar import add_menu
from ui.normalView import create_normal_view
from ui.magicView import create_magic_view
from ui.podcastView import create_podcast_view
from utils.windowState import restore_window_geometry, save_window_geometry
from classes.whisper import WHISPER  # ✅ nouvelle importation

def apply_dark_mode(widget):
    dark_bg = "#222222"
    dark_fg = "#f0f0f0"
    for child in widget.winfo_children():
        if isinstance(child, (tk.Button, tk.Label, tk.Text, tk.Frame)):
            try:
                child.configure(bg=dark_bg, fg=dark_fg)
            except Exception:
                pass
            if isinstance(child, tk.Frame):
                try:
                    child.configure(bg=dark_bg)
                except Exception:
                    pass
            apply_dark_mode(child)
    try:
        widget.configure(bg=dark_bg)
    except Exception:
        pass

def switch_mode(root, mode):
    root.ignore_geometry = True

    if hasattr(root, "mode_var"):
        root.mode_var.set(mode)

    if mode == 1:
        create_normal_view(root)
    elif mode == 2:
        create_magic_view(root)
    elif mode == 3:
        create_podcast_view(root)

    log_memory(f"Mode changé : {mode}")
    apply_dark_mode(root)
    root.after_idle(lambda: _restore_and_unlock_geometry(root))

def _restore_and_unlock_geometry(root):
    restore_window_geometry(root)
    root.after(200, lambda: setattr(root, "ignore_geometry", False))

def create_popup():
    start_timer("create_popup")
    root = tk.Tk()

    root.mode_var = tk.IntVar(value=1)

    restore_window_geometry(root)

    def on_configure(event):
        if getattr(root, "ignore_geometry", False):
            return
        save_window_geometry(root)

    root.bind("<Configure>", on_configure)

    root.title("ClipRelay")
    root.iconbitmap("img/ClipRelay.ico")

    create_normal_view(root)
    add_menu(root, changer_modele_whisper, switch_mode)
    apply_dark_mode(root)

    end_timer("create_popup")
    return root

def changer_modele_whisper(modele, root, record_btn, copy_prefix_btn, send_chatgpt_btn, show_vscode_btn):
    modele_court = modele.split("-")[-1]

    for widget in [record_btn, copy_prefix_btn, send_chatgpt_btn, show_vscode_btn]:
        widget.config(state=tk.DISABLED)

    root.status_label.config(text=f"Chargement du modèle {modele_court}...", fg="orange")
    print(f"[ClipRelay] Chargement du modèle {modele_court}")

    def load_and_reenable():
        WHISPER.load(modele)
        root.status_label.config(text=f"Modèle {modele_court} chargé !", fg="green")
        root.modele_var.set(f"Modèle : {modele_court}")
        print(f"[ClipRelay] Modèle Whisper chargé : {modele_court}")
        settings = load_user_settings()
        settings["modele"] = modele
        save_user_settings(settings)
        for widget in [record_btn, copy_prefix_btn, send_chatgpt_btn, show_vscode_btn]:
            widget.config(state=tk.NORMAL)
        root.status_label.config(text="Modèle chargé et prêt à l’emploi", fg="green")
        print("[ClipRelay] ✅ Initialisation complète : modèle Whisper prêt.")

    import threading
    threading.Thread(target=load_and_reenable).start()
