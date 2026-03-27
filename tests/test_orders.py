"""Tests de l'API commandes : création, consultation, lignes, statuts et gestion du stock."""


def test_create_order(client, client_token, sample_products):
    """Vérifie qu'un client peut créer une commande avec plusieurs lignes."""
    response = client.post(
        "/api/commandes",
        headers={"Authorization": f"Bearer {client_token}"},
        json={
            "lignes": [
                {"produit_id": sample_products[0].id, "quantite": 1},
                {"produit_id": sample_products[1].id, "quantite": 2},
            ],
            "adresse_livraison": "12 rue de la Paix, 75001 Paris",
        },
    )
    assert response.status_code == 201
    order = response.get_json()["order"]
    assert order["statut"] == "en_attente"
    assert len(order["lignes"]) == 2
    assert order["adresse_livraison"] == "12 rue de la Paix, 75001 Paris"


def test_create_order_rejects_insufficient_stock(client, client_token, sample_products):
    """Vérifie que la commande est refusée si le stock est insuffisant."""
    response = client.post(
        "/api/commandes",
        headers={"Authorization": f"Bearer {client_token}"},
        json={"lignes": [{"produit_id": sample_products[0].id, "quantite": 999}]},
    )
    assert response.status_code == 400


def test_validate_order_updates_stock(client, client_token, admin_token, sample_products):
    """Vérifie que la validation d'une commande décrémente le stock des produits."""
    create_response = client.post(
        "/api/commandes",
        headers={"Authorization": f"Bearer {client_token}"},
        json={"lignes": [{"produit_id": sample_products[0].id, "quantite": 2}]},
    )
    order_id = create_response.get_json()["order"]["id"]

    validate_response = client.patch(
        f"/api/commandes/{order_id}/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "validee"},
    )
    assert validate_response.status_code == 200

    product_response = client.get(f"/api/produits/{sample_products[0].id}")
    assert product_response.get_json()["product"]["quantite_stock"] == 3


def test_create_order_no_token(client, sample_products):
    """Vérifie que la création d'une commande sans token retourne 401."""
    response = client.post(
        "/api/commandes",
        json={"lignes": [{"produit_id": sample_products[0].id, "quantite": 1}]},
    )
    assert response.status_code == 401


def test_create_order_empty_items(client, client_token):
    """Vérifie qu'une commande avec une liste vide de lignes est refusée (400)."""
    response = client.post(
        "/api/commandes",
        headers={"Authorization": f"Bearer {client_token}"},
        json={"lignes": []},
    )
    assert response.status_code == 400


def test_create_order_invalid_product(client, client_token):
    """Vérifie qu'une commande référençant un produit inexistant retourne 404."""
    response = client.post(
        "/api/commandes",
        headers={"Authorization": f"Bearer {client_token}"},
        json={"lignes": [{"produit_id": 9999, "quantite": 1}]},
    )
    assert response.status_code == 404


def test_create_order_zero_quantity(client, client_token, sample_products):
    """Vérifie qu'une quantité de 0 dans une ligne de commande est refusée (400)."""
    response = client.post(
        "/api/commandes",
        headers={"Authorization": f"Bearer {client_token}"},
        json={"lignes": [{"produit_id": sample_products[0].id, "quantite": 0}]},
    )
    assert response.status_code == 400


def test_list_orders_no_token(client):
    """Vérifie que la liste des commandes sans token retourne 401."""
    response = client.get("/api/commandes")
    assert response.status_code == 401


def test_get_order_detail(client, client_token, sample_products):
    """Vérifie que le propriétaire peut consulter le détail de sa commande."""
    create_response = client.post(
        "/api/commandes",
        headers={"Authorization": f"Bearer {client_token}"},
        json={"lignes": [{"produit_id": sample_products[0].id, "quantite": 1}]},
    )
    order_id = create_response.get_json()["order"]["id"]

    response = client.get(f"/api/commandes/{order_id}", headers={"Authorization": f"Bearer {client_token}"})
    assert response.status_code == 200
    body = response.get_json()
    assert body["order"]["id"] == order_id
    assert body["order"]["statut"] == "en_attente"


def test_get_order_lines(client, client_token, sample_products):
    """Vérifie que la route /lignes retourne bien toutes les lignes d'une commande."""
    create_response = client.post(
        "/api/commandes",
        headers={"Authorization": f"Bearer {client_token}"},
        json={"lignes": [
            {"produit_id": sample_products[0].id, "quantite": 1},
            {"produit_id": sample_products[1].id, "quantite": 3},
        ]},
    )
    order_id = create_response.get_json()["order"]["id"]

    response = client.get(f"/api/commandes/{order_id}/lignes", headers={"Authorization": f"Bearer {client_token}"})
    assert response.status_code == 200
    lignes = response.get_json()["lignes"]
    assert len(lignes) == 2


def test_get_order_not_found(client, admin_token):
    """Vérifie que la consultation d'une commande inexistante retourne 404."""
    response = client.get("/api/commandes/9999", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 404


def test_get_order_forbidden_for_other_user(client, client_token, admin_token, sample_products):
    """Vérifie qu'un utilisateur ne peut pas consulter la commande d'un autre (403)."""
    client.post("/api/auth/register", json={"nom": "bob", "email": "bob@example.com", "password": "pass"})
    login_response = client.post("/api/auth/login", json={"email": "bob@example.com", "password": "pass"})
    bob_token = login_response.get_json()["token"]

    create_response = client.post(
        "/api/commandes",
        headers={"Authorization": f"Bearer {client_token}"},
        json={"lignes": [{"produit_id": sample_products[0].id, "quantite": 1}]},
    )
    order_id = create_response.get_json()["order"]["id"]

    response = client.get(f"/api/commandes/{order_id}", headers={"Authorization": f"Bearer {bob_token}"})
    assert response.status_code == 403


def test_update_order_status_invalid(client, admin_token, client_token, sample_products):
    """Vérifie qu'un statut invalide est refusé avec 400."""
    create_response = client.post(
        "/api/commandes",
        headers={"Authorization": f"Bearer {client_token}"},
        json={"lignes": [{"produit_id": sample_products[0].id, "quantite": 1}]},
    )
    order_id = create_response.get_json()["order"]["id"]

    response = client.patch(
        f"/api/commandes/{order_id}/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "statut_inexistant"},
    )
    assert response.status_code == 400


def test_update_order_status_non_admin(client, client_token, sample_products):
    """Vérifie qu'un client ne peut pas modifier le statut d'une commande (403)."""
    create_response = client.post(
        "/api/commandes",
        headers={"Authorization": f"Bearer {client_token}"},
        json={"lignes": [{"produit_id": sample_products[0].id, "quantite": 1}]},
    )
    order_id = create_response.get_json()["order"]["id"]

    response = client.patch(
        f"/api/commandes/{order_id}/status",
        headers={"Authorization": f"Bearer {client_token}"},
        json={"status": "validee"},
    )
    assert response.status_code == 403


def test_update_order_status_not_found(client, admin_token):
    """Vérifie que la mise à jour du statut d'une commande inexistante retourne 404."""
    response = client.patch(
        "/api/commandes/9999/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "validee"},
    )
    assert response.status_code == 404


def test_cancel_validated_order_restores_stock(client, client_token, admin_token, sample_products):
    """Vérifie que l'annulation d'une commande validée restaure le stock initial."""
    product_id = sample_products[0].id
    stock_initial = sample_products[0].quantite_stock  # 5

    order_id = client.post(
        "/api/commandes",
        headers={"Authorization": f"Bearer {client_token}"},
        json={"lignes": [{"produit_id": product_id, "quantite": 2}]},
    ).get_json()["order"]["id"]

    client.patch(
        f"/api/commandes/{order_id}/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "validee"},
    )

    stock_apres_validation = client.get(f"/api/produits/{product_id}").get_json()["product"]["quantite_stock"]
    assert stock_apres_validation == stock_initial - 2

    client.patch(
        f"/api/commandes/{order_id}/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "annulee"},
    )

    stock_final = client.get(f"/api/produits/{product_id}").get_json()["product"]["quantite_stock"]
    assert stock_final == stock_initial


def test_revalidate_cancelled_order_does_not_redecrement_stock(client, client_token, admin_token, sample_products):
    """Vérifie qu'une commande annulée puis revalidée ne décrémente pas le stock une seconde fois."""
    product_id = sample_products[0].id
    stock_initial = sample_products[0].quantite_stock  # 5

    order_id = client.post(
        "/api/commandes",
        headers={"Authorization": f"Bearer {client_token}"},
        json={"lignes": [{"produit_id": product_id, "quantite": 2}]},
    ).get_json()["order"]["id"]

    # en_attente → validee : stock passe à 3
    client.patch(
        f"/api/commandes/{order_id}/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "validee"},
    )
    # validee → annulee : stock revient à 5
    client.patch(
        f"/api/commandes/{order_id}/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "annulee"},
    )
    # annulee → validee : le stock NE doit PAS redescendre à 3 (bug rencontré en phase de développement)
    client.patch(
        f"/api/commandes/{order_id}/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "validee"},
    )

    stock_final = client.get(f"/api/produits/{product_id}").get_json()["product"]["quantite_stock"]
    assert stock_final == stock_initial  # doit rester à 5, pas redescendre à 3.


def test_validate_shipped_order_does_not_redecrement_stock(client, client_token, admin_token, sample_products):
    """Vérifie qu'une commande expédiée puis revalidée ne décrémente pas le stock une seconde fois."""
    product_id = sample_products[0].id
    stock_initial = sample_products[0].quantite_stock  # 5

    order_id = client.post(
        "/api/commandes",
        headers={"Authorization": f"Bearer {client_token}"},
        json={"lignes": [{"produit_id": product_id, "quantite": 2}]},
    ).get_json()["order"]["id"]

    # en_attente → validee : stock passe à 3
    client.patch(
        f"/api/commandes/{order_id}/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "validee"},
    )
    # validee → expediee : stock inchangé (3)
    client.patch(
        f"/api/commandes/{order_id}/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "expediee"},
    )
    # expediee → validee : le stock NE doit PAS redescendre (bug rencontré en phase de développement)
    client.patch(
        f"/api/commandes/{order_id}/status",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"status": "validee"},
    )

    stock_apres = client.get(f"/api/produits/{product_id}").get_json()["product"]["quantite_stock"]
    assert stock_apres == stock_initial - 2  # doit rester à 3, pas descendre à 1.
