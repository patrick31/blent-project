"""
Extensions Flask partagées entre tous les modules de l'application.
L'instance db est initialisée via db.init_app(app) dans la factory create_app (voir __init__.py du module app).

Réalisé pendant la préparation du projet (étape 0)
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
