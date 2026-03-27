"""Tests de l'API produits : liste, filtres, CRUD et contrôle d'accès."""


def test_list_products(client, sample_products):
    """Vérifie que la liste retourne bien les trois produits insérés en fixture."""
    response = client.get("/api/produits")
    assert response.status_code == 200
    assert len(response.get_json()["products"]) == 3


def test_create_product_as_admin(client, admin_token):
    """Vérifie qu'un admin peut créer un produit avec toutes ses données."""
    response = client.post(
        "/api/produits",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={
            "nom": "Clavier Meca",
            "description": "Clavier mécanique",
            "prix": 99.9,
            "quantite_stock": 12,
            "categorie": "peripherique",
        },
    )
    assert response.status_code == 201
    assert response.get_json()["product"]["nom"] == "Clavier Meca"


def test_create_product_as_client_forbidden(client, client_token):
    """Vérifie qu'un client ne peut pas créer un produit (403)."""
    response = client.post(
        "/api/produits",
        headers={"Authorization": f"Bearer {client_token}"},
        json={"nom": "Clavier Meca", "prix": 99.9, "quantite_stock": 12},
    )
    assert response.status_code == 403


def test_filter_products_by_category_text(client, sample_products):
    """Vérifie le filtre ?categorie= sur une partie du nom de catégorie."""
    response = client.get("/api/produits?categorie=gaming")
    assert response.status_code == 200
    body = response.get_json()
    assert len(body["products"]) == 1
    assert body["products"][0]["nom"] == "Gaming Mouse"


def test_list_products_empty(client):
    """Vérifie que la liste retourne un tableau vide quand aucun produit n'existe."""
    response = client.get("/api/produits")
    assert response.status_code == 200
    assert response.get_json()["products"] == []


def test_search_products_by_name(client, sample_products):
    """Vérifie la recherche textuelle ?trouve= sur le nom d'un produit."""
    response = client.get("/api/produits?trouve=Laptop")
    assert response.status_code == 200
    body = response.get_json()
    assert len(body["products"]) == 1
    assert body["products"][0]["nom"] == "Laptop Pro"


def test_get_product_detail(client, sample_products):
    """Vérifie que le détail d'un produit retourne ses champs corrects."""
    product_id = sample_products[0].id
    response = client.get(f"/api/produits/{product_id}")
    assert response.status_code == 200
    body = response.get_json()
    assert body["product"]["nom"] == "Laptop Pro"
    assert body["product"]["quantite_stock"] == 5


def test_get_product_not_found(client):
    """Vérifie que la consultation d'un produit inexistant retourne 404."""
    response = client.get("/api/produits/9999")
    assert response.status_code == 404


def test_create_product_no_token(client):
    """Vérifie que la création sans token retourne 401."""
    response = client.post("/api/produits", json={"nom": "Test", "prix": 10.0, "quantite_stock": 5})
    assert response.status_code == 401


def test_create_product_missing_name(client, admin_token):
    """Vérifie que la création sans nom retourne 400."""
    response = client.post(
        "/api/produits",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"prix": 99.9, "quantite_stock": 10},
    )
    assert response.status_code == 400


def test_create_product_missing_price(client, admin_token):
    """Vérifie que la création sans prix retourne 400."""
    response = client.post(
        "/api/produits",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"nom": "Produit sans prix", "quantite_stock": 10},
    )
    assert response.status_code == 400


def test_create_product_negative_price(client, admin_token):
    """Vérifie qu'un prix négatif est refusé avec 400."""
    response = client.post(
        "/api/produits",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"nom": "Produit", "prix": -5.0, "quantite_stock": 10},
    )
    assert response.status_code == 400


def test_update_product_as_admin(client, admin_token, sample_products):
    """Vérifie qu'un admin peut modifier le prix et le stock d'un produit."""
    product_id = sample_products[0].id
    response = client.put(
        f"/api/produits/{product_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"prix": 999.99, "quantite_stock": 3},
    )
    assert response.status_code == 200
    body = response.get_json()
    assert body["product"]["prix"] == 999.99
    assert body["product"]["quantite_stock"] == 3


def test_update_product_as_client_forbidden(client, client_token, sample_products):
    """Vérifie qu'un client ne peut pas modifier un produit (403)."""
    product_id = sample_products[0].id
    response = client.put(
        f"/api/produits/{product_id}",
        headers={"Authorization": f"Bearer {client_token}"},
        json={"prix": 1.0},
    )
    assert response.status_code == 403


def test_update_product_not_found(client, admin_token):
    """Vérifie que la modification d'un produit inexistant retourne 404."""
    response = client.put(
        "/api/produits/9999",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"prix": 1.0},
    )
    assert response.status_code == 404


def test_delete_product_as_admin(client, admin_token, sample_products):
    """Vérifie qu'un admin peut supprimer un produit et qu'il devient introuvable."""
    product_id = sample_products[0].id
    response = client.delete(f"/api/produits/{product_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    assert client.get(f"/api/produits/{product_id}").status_code == 404


def test_delete_product_not_found(client, admin_token):
    """Vérifie que la suppression d'un produit inexistant retourne 404."""
    response = client.delete("/api/produits/9999", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 404


def test_delete_product_as_client_forbidden(client, client_token, sample_products):
    """Vérifie qu'un client ne peut pas supprimer un produit (403)."""
    product_id = sample_products[0].id
    response = client.delete(f"/api/produits/{product_id}", headers={"Authorization": f"Bearer {client_token}"})
    assert response.status_code == 403
