"""
Fixtures pytest partagées par tous les modules de tests.
Fournit l'application de test, le client HTTP, des utilisateurs et des produits pré-créés.
"""
import pytest

from app import create_app
from app.config import TestingConfig
from app.extensions import db
from app.utils.helpers import generate_token
from app.models import Utilisateur, Produit


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


@pytest.fixture
def admin_user(app):
    """Crée et retourne un utilisateur avec le rôle admin en base de test."""
    utilisateur = Utilisateur(nom="admin", email="admin@example.com", role="admin")
    utilisateur.set_password("adminpass")
    db.session.add(utilisateur)
    db.session.commit()
    return utilisateur


@pytest.fixture
def client_user(app):
    """Crée et retourne un utilisateur avec le rôle client en base de test."""
    utilisateur = Utilisateur(nom="alice", email="alice@example.com", role="client")
    utilisateur.set_password("alicepass")
    db.session.add(utilisateur)
    db.session.commit()
    return utilisateur


@pytest.fixture
def admin_token(app, admin_user):
    """Génère et retourne un token JWT valide pour l'utilisateur admin."""
    return generate_token(admin_user)


@pytest.fixture
def client_token(app, client_user):
    """Génère et retourne un token JWT valide pour l'utilisateur client."""
    return generate_token(client_user)


@pytest.fixture
def sample_products(app):
    """Insère trois produits de test en base et les retourne sous forme de liste."""
    produits = [
        Produit(nom="Laptop Pro", description="Portable puissant", prix=1499.99,
                quantite_stock=5, categorie="ordinateur portable"),
        Produit(nom="Gaming Mouse", description="Souris précise", prix=59.90,
                quantite_stock=20, categorie="peripherique gaming"),
        Produit(nom="USB-C Dock", description="Station d'accueil", prix=129.00,
                quantite_stock=10, categorie="accessoire"),
    ]
    db.session.add_all(produits)
    db.session.commit()
    return produits
