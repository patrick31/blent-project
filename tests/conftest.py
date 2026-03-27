"""
Fixtures pytest partagées par tous les modules de tests.
Fournit l'application de test, le client HTTP, des utilisateurs et des produits pré-créés.
"""
import pytest

from app import create_app
from app.config import TestingConfig
from app.extensions import db


@pytest.fixture
def app():
    """Crée une instance de l'application Flask configurée pour les tests avec une BDD en mémoire."""
    app = create_app(TestingConfig)
    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Retourne le client de test Flask pour effectuer des requêtes HTTP simulées."""
    return app.test_client()
