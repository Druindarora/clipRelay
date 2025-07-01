from utils.userSettings import PHRASES_A_SUPPRIMER_PAR_DEFAUT


def nettoyer_texte_transcription(texte):
    """
    Supprime les phrases polluantes du texte de transcription.

    Args:
        texte (str): Le texte à nettoyer.

    Returns:
        str: Le texte nettoyé.

    Exemple:
        >>> nettoyer_texte_transcription("Merci d'utiliser Whisper.\nTranscription générée automatiquement.")
        ''
    """
    if not isinstance(texte, str):
        raise TypeError("Le texte doit être une chaîne de caractères.")

    for phrase in PHRASES_A_SUPPRIMER_PAR_DEFAUT:
        texte = texte.replace(phrase, "")
    # Optionnel : supprime les lignes vides créées
    texte = "\n".join([line for line in texte.splitlines() if line.strip() != ""])
    return texte