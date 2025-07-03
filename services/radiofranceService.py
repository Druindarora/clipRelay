import requests

# Configuration globale
API_BASE_URL = "https://api.radiofrance.fr/podcast/v1"
API_KEY = None  # À renseigner via set_api_key()

def set_api_key(key):
    global API_KEY
    API_KEY = key

def is_ready():
    return API_KEY is not None

def get_headers():
    if not is_ready():
        raise ValueError("Clé API non définie. Utilisez set_api_key().")
    return {
        "Authorization": f"Bearer {API_KEY}",
        "Accept": "application/json"
    }

# Exemple : récupérer les métadonnées d’un podcast à partir d’un ID connu
def fetch_podcast_metadata(podcast_id):
    url = f"{API_BASE_URL}/episodes/{podcast_id}"
    response = requests.get(url, headers=get_headers())
    if response.status_code == 200:
        return response.json()
    return None

# Fonction pour lister les émissions d’un podcast
def fetch_episodes_for_show(show_id, limit=5):
    url = f"{API_BASE_URL}/shows/{show_id}/episodes?limit={limit}"
    response = requests.get(url, headers=get_headers())
    if response.status_code == 200:
        return response.json().get("episodes", [])
    return []

# Recherche par mot-clé (optionnel)
def search_shows(keyword):
    url = f"{API_BASE_URL}/shows/search?query={keyword}"
    response = requests.get(url, headers=get_headers())
    if response.status_code == 200:
        return response.json().get("shows", [])
    return []
