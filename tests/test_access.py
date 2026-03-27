"""Tests d'accès à l'API: vérification de la visibilité de la banière sur la racine de l'API."""
from app import __version__


def test_api_access(client):
    """Vérifie que la banière de l'API est accessible et retourne la bonne version de l'API."""
    welcome = client.get("/", )

    assert welcome.status_code == 200
    assert welcome.get_json()["version"] == __version__
    assert welcome.get_json()["message"] == "DigiMarket API OK"


def test_user_login(client, client_token, admin_token):
    """Vérifie l'API retourne l'utilisateur connecté."""
    admin_me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {admin_token}"})
    client_me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {client_token}"})

    assert admin_me.status_code == 200
    assert admin_me.get_json()["user"]["nom"] == "admin"
    assert client_me.status_code == 200
    assert client_me.get_json()["user"]["nom"] == "alice"
