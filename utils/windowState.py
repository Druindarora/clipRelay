import os
import json
import ctypes
from ctypes import wintypes

SETTINGS_PATH = "settings.json"

def load_settings():
    if not os.path.exists(SETTINGS_PATH):
        return {}
    try:
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_settings(settings):
    try:
        with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"[windowState] Erreur lors de l'écriture : {e}")

def restore_window_geometry(root):
    settings = load_settings()
    geometry = settings.get("geometry")
    if not geometry:
        return

    try:
        root.geometry(geometry)
        root.update_idletasks()  # force le placement

        # Récupérer la position actuelle (après géometry())
        geom_str = root.geometry()  # ex : '958x980+-1927+0'
        parsed = _parse_geometry(geom_str)
        if not parsed:
            return
        size_part, x_str, y_str = parsed
        width, height = map(int, size_part.split("x"))
        x, y = int(x_str), int(y_str)

        # Récupérer la "work area" de l'écran contenant le coin supérieur gauche
        screen_workarea = _get_work_area_from_point(x, y)
        if screen_workarea:
            _, _, _, work_height = screen_workarea
            if y + height > work_height:
                height = work_height - y
                root.geometry(f"{width}x{height}+{x}+{y}")
                print(f"[windowState] Hauteur ajustée à la work area ({height}px)")

        print(f"[windowState] Géométrie restaurée : {root.geometry()}")

    except Exception as e:
        print(f"[windowState] Erreur pendant la restauration : {e}")

def save_window_geometry(root):
    settings = load_settings()
    settings["geometry"] = root.geometry()
    save_settings(settings)
    # print(f"[windowState] Géométrie sauvegardée : {settings['geometry']}")

def _parse_geometry(geom_str):
    import re
    match = re.match(r"^(\d+)x(\d+)([+-]\d+)([+-]\d+)$", geom_str)
    if not match:
        print(f"[windowState] ⚠️ Géométrie inattendue : {geom_str}")
        return None
    width, height, x_str, y_str = match.groups()
    size_part = f"{width}x{height}"
    return (size_part, x_str, y_str)


def _get_work_area_from_point(x, y):
    """
    Renvoie (left, top, right, bottom) de la zone de travail (hors barre des tâches)
    pour l'écran contenant le point (x, y)
    """
    MONITOR_DEFAULTTONEAREST = 2
    pt = wintypes.POINT(x, y)
    user32 = ctypes.windll.user32
    hmonitor = user32.MonitorFromPoint(pt, MONITOR_DEFAULTTONEAREST)

    class MONITORINFO(ctypes.Structure):
        _fields_ = [("cbSize", wintypes.DWORD),
                    ("rcMonitor", wintypes.RECT),
                    ("rcWork", wintypes.RECT),
                    ("dwFlags", wintypes.DWORD)]

    mi = MONITORINFO()
    mi.cbSize = ctypes.sizeof(mi)
    if user32.GetMonitorInfoW(hmonitor, ctypes.byref(mi)):
        work_area = mi.rcWork
        return (work_area.left, work_area.top, work_area.right, work_area.bottom)
    return None
