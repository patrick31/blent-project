"""
Configuration de l'application Flask.
Trois classes : Config (classe de base des autres configs), DevelopmentConfig et TestingConfig.

Réalisé pendant la préparation du projet (étape 0)
"""
import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
INSTANCE_DIR = BASE_DIR / "instance"


class Config:
    """Configuration de base commune à tous les environnements."""
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-secret-key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-me-jwt-secret")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{INSTANCE_DIR / 'digimarket.db'}"


class DevelopmentConfig(Config):
    """Configuration pour le développement local (mode debug activé)."""
    DEBUG = True


class TestingConfig(Config):
    """Configuration pour les tests automatisés (base SQLite en mémoire)."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    SECRET_KEY = "test-secret-key"
    JWT_SECRET_KEY = "test-jwt-secret"
