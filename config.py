from utils.clipRelayError import ClipRelayError

config = {
    'hotkey': 'ctrl+shift+f12',
    'window_size': (600, 600),
    'timeouts': {
        'window_switch': 0.5,
        'text_input': 0.1,
        'hotkey_delay': 1.5,  # délai après withdraw avant ctrl+a/ctrl+x
        'paste_delay': 0.4,    # délai après ctrl+v avant enter
        'after_paste_delay': 1.0
    },
    'focus_countdown': 5  # durée en secondes pour le décompte de focus ChatGPT
}

# Constantes globales
PHRASES_A_SUPPRIMER_PAR_DEFAUT = [
    "Merci d'utiliser Whisper.",
    "Transcription générée automatiquement."
]

# Fonction de validation des données

def validate_config(config):
    """
    Valide les données de configuration.

    Args:
        config (dict): Le dictionnaire de configuration.

    Raises:
        ClipRelayError: Si une valeur de configuration est invalide.
    """
    if not isinstance(config, dict):
        raise ClipRelayError("La configuration doit être un dictionnaire.")

    if 'hotkey' not in config or not isinstance(config['hotkey'], str):
        raise ClipRelayError("La touche de raccourci doit être une chaîne de caractères.")

    if 'window_size' not in config or not isinstance(config['window_size'], tuple):
        raise ClipRelayError("La taille de la fenêtre doit être un tuple.")

    if 'timeouts' not in config or not isinstance(config['timeouts'], dict):
        raise ClipRelayError("Les délais doivent être définis dans un dictionnaire.")

    for key, value in config['timeouts'].items():
        if not isinstance(value, (int, float)):
            raise ClipRelayError(f"Le délai '{key}' doit être un nombre.")

validate_config(config)