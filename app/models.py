"""
Modèles SQLAlchemy de DigiMarket.
Définit les quatres classes du modèle de données : Utilisateur, Produit, Commande, LigneCommande.
Des méthodes utilitaires spécifiques au modèle de donnée sont ajoutées dans les classes lorsque nécessaire.

Réalisé pendant l'étape 1 du projet et étendu à l'étape 2.
"""
from datetime import datetime, timezone

from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db


# Etape 1
class Utilisateur(db.Model):
    """Représente un compte utilisateur (client ou admin)."""

    __tablename__ = "utilisateurs"

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    mot_de_passe = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="client")
    date_creation = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    def set_password(self, password: str) -> None:
        """Hache le mot de passe en clair et le stocke dans mot_de_passe."""
        self.mot_de_passe = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Vérifie si le mot de passe en clair correspond au hash stocké."""
        return check_password_hash(self.mot_de_passe, password)

    def to_dict(self) -> dict:
        """Retourne une représentation dictionnaire sérialisable en JSON."""
        return {
            "id": self.id,
            "nom": self.nom,
            "email": self.email,
            "role": self.role,
            "date_creation": self.date_creation.isoformat(),
        }


# Etape 2
class Produit(db.Model):
    """Représente un produit du catalogue DigiMarket."""

    __tablename__ = "produits"

    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    categorie = db.Column(db.String(120), nullable=True)
    prix = db.Column(db.Float, nullable=False)
    quantite_stock = db.Column(db.Integer, nullable=False, default=0)
    date_creation = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nom": self.nom,
            "description": self.description,
            "categorie": self.categorie,
            "prix": self.prix,
            "quantite_stock": self.quantite_stock,
            "date_creation": self.date_creation.isoformat(),
        }
