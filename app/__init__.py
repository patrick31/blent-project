"""
Point d'entrée de l'application Flask DigiMarket.
Contient la factory create_app qui initialise la base de données et enregistre les Blueprints.

Réalisé pendant la préparation du projet (étape 0)
"""
from flask import Flask

__version__ = "1.0.1"

from .config import DevelopmentConfig
from .extensions import db
from .utils.helpers import json_message


# Etape 0
def create_app(config_class=None):
    """Crée et configure l'application Flask selon la classe de configuration fournie."""

    if config_class is None:
        config_class = DevelopmentConfig
        print("Configuration non précisée, utilise 'DevelopmentConfig' par défaut.")

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.get("/")
    def healthcheck():
        """ Message test de fonctionnement de l'APi sur la route principale ajouté à la création de l'application."""
        return json_message("DigiMarket API OK", version=__version__)

    return app
