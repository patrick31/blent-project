"""
Point d'entrée de l'application Flask DigiMarket.
Contient la factory create_app qui initialise la base de données et enregistre les Blueprints.

Réalisé pendant la préparation du projet (étape 0)
"""
import sys
from pathlib import Path

from flask import Flask

__version__ = "1.5.0"

from .config import DevelopmentConfig
from .extensions import db
from .utils.helpers import json_message
from .auth.routes import auth_bp
from .products.routes import products_bp
from .orders.routes import orders_bp


# Etape 0
def create_app(config_class=None):
    """Crée et configure l'application Flask selon la classe de configuration fournie."""

    if config_class is None:
        config_class = DevelopmentConfig
        print("Configuration non précisée, utilise 'DevelopmentConfig' par défaut.")

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    db.init_app(app)

    uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    if uri.startswith("sqlite:///") and uri != "sqlite:///:memory:":
        db_path = Path(uri.removeprefix("sqlite:///"))
        if not db_path.exists():
            print("ERREUR : la base de données est introuvable.")
            print(f"  Chemin attendu : {db_path}")
            print()
            print("  Lancez d'abord : python seed.py")
            sys.exit(1)

    with app.app_context():
        db.create_all()

    app.register_blueprint(auth_bp)
    app.register_blueprint(products_bp)  # Etape 2
    app.register_blueprint(orders_bp)  # Etape 3

    @app.get("/")
    def healthcheck():
        """ Message test de fonctionnement de l'APi sur la route principale ajouté à la création de l'application."""
        return json_message("DigiMarket API OK", version=__version__)

    return app
