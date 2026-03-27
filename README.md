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
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Installer les dépendances
pip install -r requirements.txt
```

## Démarrage

# Lancer le serveur : main fait app.run(debug=True)
python run.py
```

ou aussi :

```shell
# configuration dans .flaskenv
flask run --debug
```

L'API est accessible sur `http://localhost:5001`.

