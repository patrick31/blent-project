"""Tests de contrôle d'accès : vérification de la séparation des données entre utilisateurs."""


def test_client_can_only_see_own_orders(client, client_token, admin_token, sample_products):
    """Vérifie qu'un client ne voit que ses propres commandes, tandis que l'admin les voit toutes."""
    client.post(
        "/api/commandes",
        headers={"Authorization": f"Bearer {client_token}"},
        json={"lignes": [{"produit_id": sample_products[0].id, "quantite": 1}]},
    )

    admin_list = client.get("/api/commandes", headers={"Authorization": f"Bearer {admin_token}"})
    client_list = client.get("/api/commandes", headers={"Authorization": f"Bearer {client_token}"})

    assert admin_list.status_code == 200
    assert client_list.status_code == 200
    assert len(admin_list.get_json()["orders"]) >= 1
    assert len(client_list.get_json()["orders"]) == 1
