# DigiMarket API

Projet d'API REST e-commerce avec Flask, SQLAlchemy, JWT et pytest développée dans le cadre de la formation Blent AI.

## Fonctionnalités prévues

- Authentification utilisateur
- Gestion des produits
- Gestion des commandes
- Contrôle d'accès admin / client
- Tests automatisés avec pytest

## Stack technique

- **Python 3.x**
- **Flask** — framework web
- **SQLAlchemy** — ORM
- **SQLite** — base de données
- **JWT (PyJWT)** — authentification par token

## Installation

```bash
# Cloner le projet
git clone https://github.com/patrick31/blent-project.git
cd blent-project

# Créer et activer l'environnement virtuel
python -m venv .venv
source .venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt
```

## Démarrage

```bash
# Initialiser la base (nécessaire avant de lancer le serveur) avec ajout des données de test (nécessaire pour avoir un admin)
python seed.py

# Lancer le serveur : main() appelle la factory create_app() et fait app.run(debug=True)
python run.py
```

ou aussi :

```shell
# configuration dans .flaskenv (mode debug + port)
flask run
```

L'API est accessible sur `http://localhost:5001`.

> [!TIP]
>
> Pour tester l'API sans passer par les tests automatiques pytest, utiliser le mini frontend "cli.py" (voir ci-dessous).



## Frontend de tests manuels en CLI

Un client en ligne de commande permet de tester toutes les fonctionnalités de l'API manuellement de façon interactive. Il nécessite la bibliothèque `requests` :

```bash
pip install requests
```

Lancer le serveur dans un terminal, puis dans une (ou plusieurs) autre(s) fenêtre(s) lancer le(s) client(s) :

```bash
python cli.py
```

Le client CLI propose un menu texte pour se connecter ou créer un compte, puis accéder à toutes les routes de l'API.

> [!WARNING]
>
> _**Attention** : pour fonctionner le client CLI nécessite qu'une base de démo avec un admin soit créé avec seed.py et que le serveur soit lancé avant dans une autre fenêtre avec run.py._



## Tests automatiques

Les tests automatiques utilisent leur propre base de test en mémoire, il n'est donc pas nécessaire de lancer seed.py avant les tests.

Ils nécessitent la bibliothèque `pytest` :

```bash
pip install pytest
```

Lancer les tests :

```bash
pytest tests/ -v
```





---

## Documentation de l'API

### Authentification

| Méthode | Endpoint | Description | Auth |
|---------|----------|-------------|------|
| POST | `/api/auth/register` | Créer un compte | Non |
| POST | `/api/auth/login` | Se connecter, obtenir un token JWT | Non |
| GET | `/api/auth/me` | Profil de l'utilisateur connecté | Token |

#### POST `/api/auth/register`
```json
{
  "nom": "alice",
  "email": "alice@example.com",
  "password": "motdepasse"
}
```
> [!NOTE]
>
> Le rôle est toujours `client`. Les comptes `admin` sont créés uniquement via `seed.py`.

#### POST `/api/auth/login`

L'identifiant peut être l'email **ou** le nom d'utilisateur :

```json
{ "email": "alice@example.com", "password": "alice1234" }
```
```json
{ "nom": "alice", "password": "alice1234" }
```
Retourne un `token` JWT à inclure dans les requêtes suivantes :
```
Authorization: Bearer <token>
```

---

### Produits

| Méthode | Endpoint | Description | Auth |
|---------|----------|-------------|------|
| GET | `/api/produits` | Lister les produits | Non |
| GET | `/api/produits/{id}` | Détail d'un produit | Non |
| POST | `/api/produits` | Créer un produit | Admin |
| PUT | `/api/produits/{id}` | Modifier un produit | Admin |
| DELETE | `/api/produits/{id}` | Supprimer un produit | Admin |

#### Paramètres de recherche (GET `/api/produits`)
- `?trouve=clavier` — recherche "clavier" dans le nom et la description
- `?categorie=gaming` — filtre par la catégorie "gaming" (recherche partielle)

#### POST / PUT `/api/produits`
```json
{
  "nom": "Laptop Pro",
  "description": "Portable haute performance",
  "prix": 1499.99,
  "quantite_stock": 10,
  "categorie": "ordinateur portable"
}
```

---

### Commandes

| Méthode | Endpoint | Description | Auth |
|---------|----------|-------------|------|
| POST | `/api/commandes` | Créer une commande | Token |
| GET | `/api/commandes` | Lister les commandes | Token |
| GET | `/api/commandes/{id}` | Détail d'une commande | Token |
| GET | `/api/commandes/{id}/lignes` | Lignes d'une commande | Token |
| PATCH | `/api/commandes/{id}/status` | Modifier le statut | Admin |

> [!CAUTION]
>
> Un client ne voit que ses propres commandes. Un admin voit toutes les commandes.

#### POST `/api/commandes`
```json
{
  "adresse_livraison": "12 rue de la Paix, 75001 Paris",
  "lignes": [
    {"produit_id": 1, "quantite": 2},
    {"produit_id": 3, "quantite": 1}
  ]
}
```

#### PATCH `/api/commandes/{id}/status`
```json
{
  "status": "validee"
}
```
Statuts possibles : `en_attente`, `validee`, `expediee`, `annulee`.

> [!IMPORTANT]
>
> La validation d'une commande décrémente automatiquement le stock des produits.
> L'annulation d'une commande validée restaure le stock.



---

## Structure du projet

```
blent-project/
├── app/
│   ├── __init__.py             # Factory create_app
│   ├── config.py               # Configurations (Dev, Test)
│   ├── extensions.py           # Instance SQLAlchemy
│   ├── models.py               # Modèles Utilisateur, Produit, Commande, LigneCommande
│   ├── auth/
│   │   └── routes.py           # Blueprint /api/auth
│   ├── products/
│   │   └── routes.py           # Blueprint /api/produits
│   ├── orders/
│   │   └── routes.py           # Blueprint /api/commandes
│   └── utils/
│       ├── helpers.py          # JWT, réponses JSON
│       └── decorators.py       # token_required, admin_required
├── tests/
│   ├── conftest.py             # Fixtures pytest pour les différents tests ci-dessous
│   ├── test_access.py          # Teste le fonctionnement de l'API 
│   ├── test_auth.py            # Teste les API d'authentification
│   ├── test_products.py        # Teste les API sur les produits
│   ├── test_orders.py          # Teste les API sur les commandes
│   └── test_access_control.py  # Teste l'efficacité du contrôle d'accès
├── seed.py                     # Données de démo (par exemple pour utiliser la CLI)
├── run.py                      # Point d'entrée pour lancer le serveur
├── cli.py                      # Point d'entrée pour lancer le serveur
├── pytest.ini                  # configuration de pytest
├── .flaskenv                   # configuration de flask si lancement direct avec "flast run"
└── requirements.txt            # Liste des modules python à installer pour le serveur
```

### Principe

- Flask Application Factory : create_app() dans `__init.py__` lancé par run.py

  Création de l'applcation WSGI à la demande avec la configuration adaptée (debug, pytest, etc.)

- Blueprints Flask : séparation fonctionnelle des routes : auth / products / orders

- SQLAlchemy : ORM

- pytest : tests isolés automatisé (dossier /tests)

### extensions.py

```python
db = SQLAlchemy()
```

Permet d'éviter les imports circulaires.

------------------------------------------------------------------------

### config.py

-   DevelopmentConfig
-   TestingConfig

Contient : 

- DB URI
- JWT secret
- flags

------------------------------------------------------------------------

## Modèle de données

### models.py

Définition des modèles de données pour l'ORM

### Utilisateur
| Champ | Type | Description |
|-------|------|-------------|
| id | Integer | Clé primaire |
| nom | String | Nom de l'utilisateur (unique) |
| email | String | Email unique |
| mot_de_passe | String | Mot de passe haché |
| role | String | `client` ou `admin` |
| date_creation | DateTime | Date de création |

### Produit
| Champ | Type | Description |
|-------|------|-------------|
| id | Integer | Clé primaire |
| nom | String | Nom du produit |
| description | Text | Description |
| categorie | String | Catégorie |
| prix | Float | Prix unitaire |
| quantite_stock | Integer | Quantité en stock |
| date_creation | DateTime | Date d'ajout |

### Commande
| Champ | Type | Description |
|-------|------|-------------|
| id | Integer | Clé primaire |
| utilisateur_id | Integer | FK → Utilisateur |
| statut | String | `en_attente`, `validee`, `expediee`, `annulee` |
| montant_total | Float | Montant total calculé |
| adresse_livraison | String | Adresse de livraison |
| date_commande | DateTime | Date de commande |

### LigneCommande
| Champ | Type | Description |
|-------|------|-------------|
| id | Integer | Clé primaire |
| commande_id | Integer | FK → Commande |
| produit_id | Integer | FK → Produit |
| quantite | Integer | Quantité commandée |
| prix_unitaire | Float | Prix au moment de la commande |

## Conclusion

Bien que ce projet soit pédagogique dans le cadre des HandsOn de la formation Blent son architecture modulaire, testable, extensible, est réalisée comme pour un projet professionnel.
