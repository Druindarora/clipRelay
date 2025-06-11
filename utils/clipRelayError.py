class ClipRelayError(Exception):
    """Classe de base pour les erreurs de ClipRelay"""
    def __init__(self, message="Une erreur est survenue dans ClipRelay"):
        self.message = message
        super().__init__(self.message)

class WindowNotFoundError(ClipRelayError):
    """Erreur levée quand une fenêtre n'est pas trouvée"""
    def __init__(self, window_name):
        self.window_name = window_name
        message = f"La fenêtre '{self.window_name}' n'a pas été trouvée."
        super().__init__(message)

class ClipboardError(ClipRelayError):
    """Erreur levée lors d'un problème avec le presse-papiers"""
    def __init__(self, error_detail):
        self.error_detail = error_detail
        message = f"Problème avec le presse-papiers : {self.error_detail}"
        super().__init__(message)

class TimeoutError(ClipRelayError):
    """Erreur levée lors d'un timeout"""
    def __init__(self, operation, timeout_duration):
        self.operation = operation
        self.timeout_duration = timeout_duration
        message = f"Le timeout s'est produit pour l'opération '{self.operation}'. Temps de délai : {self.timeout_duration} secondes."
        super().__init__(message)