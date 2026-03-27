#!/usr/bin/env python3
"""
DigiMarket CLI — Interface FrontEnd en ligne de commande pour tester l'API sans passer par le client Flask.
Ce script nécessite l'installation de la bibliothèque requests : pip install requests

Usage : python cli.py

Remarque : Il est possible de lancer plusieurs instances de la CLI pour tester plusieurs connexions en paralelles.

"""
import json
import sys

try:
    import requests
except ImportError:
    print("[ERREUR] Le module 'requests' est introuvable.")
    print("  Installez-le avec : pip install requests")
    sys.exit(1)

# l'url et le port doivent correspondre à ce qui est dans le serveur Flask (voir run.py).
BASE_URL = "http://localhost:5001"
token = None
current_user = None


# ── Utilitaires ───────────────────────────────────────────────────────────────


def fmt_json(data):
    """Affiche un objet JSON indenté."""
    print(json.dumps(data, ensure_ascii=False, indent=2))


def api(method, path, **kwargs):
    """Effectue un appel API et retourne (status_code, data)."""
    headers = kwargs.pop("headers", {})
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        resp = requests.request(method, BASE_URL + path, headers=headers, **kwargs)
        try:
            data = resp.json()
        except Exception:
            data = {"raw": resp.text}
        return resp.status_code, data
    except requests.ConnectionError:
        print(f"\n  [ERREUR] Impossible de joindre {BASE_URL}. Le serveur est-il lancé ?")
        return None, None


def ask(prompt, optional=False):
    """Pose une question, retourne None si vide et optional=True."""
    suffix = " (Entrée pour ignorer)" if optional else ""
    val = input(f"  {prompt}{suffix} : ").strip()
    if optional and not val:
        return None
    return val


def ask_product_id(prompt="ID du produit"):
    """Demande un ID produit, '?' affiche la liste des produits."""
    while True:
        val = input(f"  {prompt} (? pour lister, Entrée pour annuler) : ").strip()
        if val == "?":
            status, data = api("GET", "/api/produits")
            if data and "products" in data:
                print()
                for p in data["products"]:
                    print(f"  {json.dumps(p, ensure_ascii=False)}")
                print()
        elif val == "":
            return None
        else:
            try:
                return int(val)
            except ValueError:
                print("  ID invalide, entrez un nombre entier.")


def ask_order_id(prompt="ID de la commande"):
    """Demande un ID commande, '?' affiche la liste des commandes."""
    while True:
        val = input(f"  {prompt} (? pour lister, Entrée pour annuler) : ").strip()
        if val == "?":
            status, data = api("GET", "/api/commandes")
            if data and "orders" in data:
                print()
                for c in data["orders"]:
                    print(f"  {json.dumps(c, ensure_ascii=False)}")
                print()
        elif val == "":
            return None
        else:
            try:
                return int(val)
            except ValueError:
                print("  ID invalide, entrez un nombre entier.")


# ── Auth ──────────────────────────────────────────────────────────────────────


def do_register():
    print("\n── Créer un compte ──")
    nom = ask("Nom d'utilisateur")
    email = ask("Email")
    password = ask("Mot de passe")
    status, data = api("POST", "/api/auth/register", json={
        "nom": nom, "email": email, "password": password,
    })
    print(f"\n  HTTP {status}")
    fmt_json(data)


def do_login():
    global token, current_user
    print("\n── Connexion ──")
    identifiant = ask("Email ou nom d'utilisateur")
    password = ask("Mot de passe")
    status, data = api("POST", "/api/auth/login", json={"email": identifiant, "password": password})
    print(f"\n  HTTP {status}")
    fmt_json(data)
    if status == 200 and data and "token" in data:
        token = data["token"]
        _, me = api("GET", "/api/auth/me")
        current_user = me.get("user") if me else None
        if current_user:
            print(f"\n  Connecté : {current_user['nom']} ({current_user['role']})")
        return True
    return False


def auth_menu():
    while True:
        print("\n╔══════════════════════════════╗")
        print("║       DigiMarket CLI         ║")
        print("╚══════════════════════════════╝")
        print("  1. Se connecter       (POST /api/auth/login)")
        print("  2. Créer un compte    (POST /api/auth/register)")
        print("  0. Quitter")
        choice = input("\n  Choix : ").strip()
        if choice == "1":
            if do_login():
                return
        elif choice == "2":
            do_register()
        elif choice == "0":
            sys.exit(0)


# ── Actions API ───────────────────────────────────────────────────────────────


def action_me():
    status, data = api("GET", "/api/auth/me")
    print(f"\n  HTTP {status}")
    fmt_json(data)


def action_list_products():
    print("\n── Lister les produits ──")
    trouve = ask("Recherche texte (nom/description)", optional=True)
    categorie = ask("Filtrer par catégorie", optional=True)
    params = {}
    if trouve:
        params["trouve"] = trouve
    if categorie:
        params["categorie"] = categorie
    status, data = api("GET", "/api/produits", params=params)
    print(f"\n  HTTP {status}")
    if data and "products" in data:
        for p in data["products"]:
            print(json.dumps(p, ensure_ascii=False))
    else:
        fmt_json(data)


def action_get_product():
    print("\n── Détail d'un produit ──")
    pid = ask_product_id()
    if not pid:
        return
    status, data = api("GET", f"/api/produits/{pid}")
    print(f"\n  HTTP {status}")
    fmt_json(data)


def action_create_product():
    print("\n── Créer un produit ──")
    nom = ask("Nom")
    description = ask("Description", optional=True)
    prix_str = ask("Prix")
    quantite_str = ask("Quantité en stock")
    categorie = ask("Catégorie", optional=True)
    payload = {}
    if nom:
        payload["nom"] = nom
    if description:
        payload["description"] = description
    if prix_str:
        try:
            payload["prix"] = float(prix_str)
        except ValueError:
            print("  Prix invalide.")
            return
    if quantite_str:
        try:
            payload["quantite_stock"] = int(quantite_str)
        except ValueError:
            print("  Quantité invalide.")
            return
    if categorie:
        payload["categorie"] = categorie
    status, data = api("POST", "/api/produits", json=payload)
    print(f"\n  HTTP {status}")
    fmt_json(data)


def action_update_product():
    print("\n── Modifier un produit ──")
    pid = ask_product_id()
    if not pid:
        return
    print("  (Entrée pour conserver la valeur actuelle)")
    nom = ask("Nouveau nom", optional=True)
    description = ask("Nouvelle description", optional=True)
    prix_str = ask("Nouveau prix", optional=True)
    quantite_str = ask("Nouvelle quantité en stock", optional=True)
    categorie = ask("Nouvelle catégorie", optional=True)
    payload = {}
    if nom:
        payload["nom"] = nom
    if description:
        payload["description"] = description
    if prix_str:
        try:
            payload["prix"] = float(prix_str)
        except ValueError:
            print("  Prix invalide.")
            return
    if quantite_str:
        try:
            payload["quantite_stock"] = int(quantite_str)
        except ValueError:
            print("  Quantité invalide.")
            return
    if categorie:
        payload["categorie"] = categorie
    status, data = api("PUT", f"/api/produits/{pid}", json=payload)
    print(f"\n  HTTP {status}")
    fmt_json(data)


def action_delete_product():
    print("\n── Supprimer un produit ──")
    pid = ask_product_id()
    if not pid:
        return
    confirm = input(f"  Confirmer la suppression du produit {pid} ? (o/N) : ").strip().lower()
    if confirm != "o":
        print("  Annulé.")
        return
    status, data = api("DELETE", f"/api/produits/{pid}")
    print(f"\n  HTTP {status}")
    fmt_json(data)


def action_list_orders():
    print("\n── Lister les commandes ──")
    status, data = api("GET", "/api/commandes")
    print(f"\n  HTTP {status}")
    if data and "orders" in data:
        for c in data["orders"]:
            print(json.dumps(c, ensure_ascii=False))
    else:
        fmt_json(data)


def action_get_order():
    print("\n── Détail d'une commande ──")
    oid = ask_order_id()
    if not oid:
        return
    status, data = api("GET", f"/api/commandes/{oid}")
    print(f"\n  HTTP {status}")
    fmt_json(data)


def action_get_order_lines():
    print("\n── Lignes d'une commande ──")
    oid = ask_order_id()
    if not oid:
        return
    status, data = api("GET", f"/api/commandes/{oid}/lignes")
    print(f"\n  HTTP {status}")
    if data and "lignes" in data:
        for ligne in data["lignes"]:
            print(json.dumps(ligne, ensure_ascii=False))
    else:
        fmt_json(data)


def action_create_order():
    print("\n── Créer une commande ──")
    adresse = ask("Adresse de livraison", optional=True)
    lignes = []
    print("  Ajout des articles (Entrée sans ID pour terminer) :")
    while True:
        pid = ask_product_id("  ID produit")
        if not pid:
            break
        quantite_str = ask("  Quantité")
        try:
            quantite = int(quantite_str)
        except (ValueError, TypeError):
            print("  Quantité invalide, article ignoré.")
            continue
        lignes.append({"produit_id": pid, "quantite": quantite})
        print(f"  → Article ajouté ({len(lignes)} au total)")
    if not lignes:
        print("  Aucun article, commande annulée.")
        return
    payload = {"lignes": lignes}
    if adresse:
        payload["adresse_livraison"] = adresse
    status, data = api("POST", "/api/commandes", json=payload)
    print(f"\n  HTTP {status}")
    fmt_json(data)


def action_update_order_status():
    print("\n── Modifier le statut d'une commande ──")
    oid = ask_order_id()
    if not oid:
        return
    print("  Statuts : en_attente, validee, expediee, annulee")
    statut = ask("Nouveau statut")
    if not statut:
        return
    status, data = api("PATCH", f"/api/commandes/{oid}/status", json={"status": statut})
    print(f"\n  HTTP {status}")
    fmt_json(data)


# ── Menu principal ────────────────────────────────────────────────────────────

MENU = [
    ("── Authentification ──", None),
    ("Mon profil                (GET /api/auth/me)", action_me),
    ("── Produits ──", None),
    ("Lister les produits       (GET /api/produits)", action_list_products),
    ("Détail d'un produit       (GET /api/produits/{id})", action_get_product),
    ("Créer un produit          (POST /api/produits)", action_create_product),
    ("Modifier un produit       (PUT /api/produits/{id})", action_update_product),
    ("Supprimer un produit      (DELETE /api/produits/{id})", action_delete_product),
    ("── Commandes ──", None),
    ("Créer une commande        (POST /api/commandes)", action_create_order),
    ("Lister les commandes      (GET /api/commandes)", action_list_orders),
    ("Détail d'une commande     (GET /api/commandes/{id})", action_get_order),
    ("Lignes d'une commande     (GET /api/commandes/{id}/lignes)", action_get_order_lines),
    ("Modifier statut commande  (PATCH /api/commandes/{id}/status)", action_update_order_status),
]


def main_menu():
    global token, current_user
    menu = MENU

    while True:
        user_label = f"{current_user['nom']} [{current_user['role']}]" if current_user else ""
        print(f"\n╔══════════════════════════════════╗")
        print(f"║  DigiMarket  {user_label:<20}║")
        print(f"╚══════════════════════════════════╝")
        num = 0
        index_map = {}
        for label, action in menu:
            if action is None:
                print(f"  {label}")
            else:
                num += 1
                index_map[num] = action
                print(f"  {num:2}. {label}")
        print("   0. Se déconnecter")

        choice = input("\n  Choix : ").strip()
        if choice == "0":
            token = None
            current_user = None
            print("  Déconnecté.")
            return
        try:
            idx = int(choice)
            if idx in index_map:
                index_map[idx]()
            else:
                print("  Choix invalide.")
        except ValueError:
            print("  Choix invalide.")


def main():
    print(f"  Serveur cible : {BASE_URL}")
    status, data = api("GET", "/")
    if status is None:
        print("  [ERREUR] Serveur inaccessible. Lancez d'abord : python run.py")
        sys.exit(1)
    elif data and "message" in data:
        print(f"  HTTP {status}  {json.dumps(data, ensure_ascii=False)}")
    else:
        print(f"  [ATTENTION] Réponse inattendue (HTTP {status}). Le serveur DigiMarket est-il bien lancé ?")
        sys.exit(1)
    print()
    while True:
        auth_menu()
        main_menu()


if __name__ == "__main__":
    main()
