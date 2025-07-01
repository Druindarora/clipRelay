import json
import os
from utils.clipRelayError import ClipRelayError

SETTINGS_FILE = "settings.json"
DUREE_ENREGISTREMENT_PAR_DEFAUT = 60

# Définition des labels de mode (utilisés dans l'UI)
MODE_LABELS = {
    1: "Mode normal",
    2: "Mode anti-pollution"
}

def load_user_settings():
    """
    Charge les paramètres utilisateur depuis un fichier JSON.

    Returns:
        dict: Les paramètres utilisateur.

    Raises:
        ClipRelayError: Si le fichier JSON est corrompu ou illisible.
    """
    try:
        if os.path.exists(SETTINGS_FILE):
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                settings = json.load(f)
        else:
            settings = {}
        # Valeur par défaut si absente
        if "duree_enregistrement" not in settings:
            settings["duree_enregistrement"] = DUREE_ENREGISTREMENT_PAR_DEFAUT
        if "mode" not in settings:
            settings["mode"] = 1  # Mode normal par défaut
        return settings
    except json.JSONDecodeError as e:
        raise ClipRelayError(f"Erreur de lecture du fichier JSON : {e}")

def save_user_settings(settings):
    """
    Sauvegarde les paramètres utilisateur dans un fichier JSON.

    Args:
        settings (dict): Les paramètres utilisateur à sauvegarder.

    Raises:
        ClipRelayError: Si une erreur survient lors de l'écriture du fichier.
    """
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
    except Exception as e:
        raise ClipRelayError(f"Erreur de sauvegarde des paramètres utilisateur : {e}")
