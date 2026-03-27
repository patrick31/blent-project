"""Tests de l'API d'authentification : inscription, connexion et profil utilisateur."""


def test_register_success(client):
    """Vérifie qu'un utilisateur peut s'inscrire avec des données valides."""
    response = client.post(
        "/api/auth/register",
        json={
            "nom": "bob",
            "email": "bob@example.com",
            "password": "secret123",
            "role": "client",
        },
    )
    assert response.status_code == 201
    body = response.get_json()
    assert body["user"]["nom"] == "bob"


def test_login_success(client):
    """Vérifie qu'un utilisateur enregistré peut se connecter et reçoit un token."""
    client.post(
        "/api/auth/register",
        json={"nom": "bob", "email": "bob@example.com", "password": "secret123"},
    )
    response = client.post(
        "/api/auth/login",
        json={"email": "bob@example.com", "password": "secret123"},
    )
    assert response.status_code == 200
    assert "token" in response.get_json()


def test_me_requires_token(client):
    """Vérifie que /me retourne 401 sans token."""
    response = client.get("/api/auth/me")
    assert response.status_code == 401


def test_me_returns_profile(client, client_token):
    """Vérifie que /me retourne le profil de l'utilisateur authentifié."""
    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {client_token}"})
    assert response.status_code == 200
    body = response.get_json()
    assert body["user"]["nom"] == "alice"
    assert body["user"]["role"] == "client"


def test_register_duplicate_email(client):
    """Vérifie que l'inscription avec un email déjà utilisé retourne 409."""
    client.post("/api/auth/register", json={"nom": "bob", "email": "bob@example.com", "password": "secret123"})
    response = client.post("/api/auth/register",
                           json={"nom": "bob2", "email": "bob@example.com", "password": "secret123"})
    assert response.status_code == 409


def test_register_duplicate_nom(client):
    """Vérifie que l'inscription avec un nom déjà utilisé retourne 409."""
    client.post("/api/auth/register", json={"nom": "bob", "email": "bob@example.com", "password": "secret123"})
    response = client.post("/api/auth/register",
                           json={"nom": "bob", "email": "bob2@example.com", "password": "secret123"})
    assert response.status_code == 409


def test_register_missing_fields(client):
    """Vérifie que l'inscription avec des champs manquants retourne 400."""
    response = client.post("/api/auth/register", json={"nom": "bob"})
    assert response.status_code == 400


def test_register_role_always_client(client):
    """Vérifie que le rôle est toujours 'client' même si 'admin' est envoyé."""
    response = client.post(
        "/api/auth/register",
        json={"nom": "bob", "email": "bob@example.com", "password": "secret123", "role": "admin"},
    )
    assert response.status_code == 201
    assert response.get_json()["user"]["role"] == "client"


def test_login_wrong_password(client):
    """Vérifie que la connexion avec un mauvais mot de passe retourne 401."""
    client.post("/api/auth/register", json={"nom": "bob", "email": "bob@example.com", "password": "secret123"})
    response = client.post("/api/auth/login", json={"email": "bob@example.com", "password": "wrongpassword"})
    assert response.status_code == 401


def test_login_unknown_email(client):
    """Vérifie que la connexion avec un email inconnu retourne 401."""
    response = client.post("/api/auth/login", json={"email": "nobody@example.com", "password": "secret123"})
    assert response.status_code == 401


def test_login_missing_fields(client):
    """Vérifie que la connexion sans fournir un mot de passe retourne 400."""
    response = client.post("/api/auth/login", json={"email": "bob@example.com"})
    assert response.status_code == 400


def test_me_invalid_token(client):
    """Vérifie que /me avec un token invalide retourne 401."""
    response = client.get("/api/auth/me", headers={"Authorization": "Bearer tokenbidon"})
    assert response.status_code == 401
