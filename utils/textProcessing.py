def nettoyer_texte_transcription(texte):
    """
    Nettoie le texte de transcription en supprimant les lignes vides et les espaces inutiles.

    Args:
        texte (str): Le texte à nettoyer.

    Returns:
        str: Le texte nettoyé.
    """
    if not isinstance(texte, str):
        raise TypeError("Le texte doit être une chaîne de caractères.")

    # Supprime les lignes vides et les espaces inutiles
    texte = "\n".join([line.strip() for line in texte.splitlines() if line.strip() != ""])
    return texte