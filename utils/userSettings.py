import json
import os

SETTINGS_FILE = "settings.json"
DUREE_ENREGISTREMENT_PAR_DEFAUT = 60
PHRASES_A_SUPPRIMER_PAR_DEFAUT = []

# Définition des labels de mode (utilisés dans l'UI)
MODE_LABELS = {
    1: "Mode normal",
    2: "Mode anti-pollution"
}

def load_user_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            settings = json.load(f)
    else:
        settings = {}
    # Valeur par défaut si absente
    if "duree_enregistrement" not in settings:
        settings["duree_enregistrement"] = DUREE_ENREGISTREMENT_PAR_DEFAUT
    if "phrases_a_supprimer" not in settings:
        settings["phrases_a_supprimer"] = PHRASES_A_SUPPRIMER_PAR_DEFAUT
    if "mode" not in settings:
        settings["mode"] = 1  # Mode normal par défaut
    return settings

def save_user_settings(settings):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)