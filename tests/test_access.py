"""Tests d'accès à l'API: vérification de la visibilité de la banière sur la racine de l'API."""
from app import __version__


def test_api_access(client):
    """Vérifie que la banière de l'API est accessible et retourne la bonne version de l'API."""
    welcome = client.get("/", )

    assert welcome.status_code == 200
    assert welcome.get_json()["version"] == __version__
    assert welcome.get_json()["message"] == "DigiMarket API OK"
