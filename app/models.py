"""
Modèles SQLAlchemy de DigiMarket.
Définit les quatres classes du modèle de données : Utilisateur, Produit, Commande, LigneCommande.
Des méthodes utilitaires spécifiques au modèle de donnée sont ajoutées dans les classes lorsque nécessaire.

Réalisé pendant l'étape 1 du projet et étendu à l'étape 2 et 3.
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

    # Ajoout étape 3
    commandes = db.relationship("Commande", back_populates="utilisateur", cascade="all, delete-orphan")

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

    # Ajoout étape 3
    lignes_commande = db.relationship("LigneCommande", back_populates="produit")

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


# Etape 3
class Commande(db.Model):
    """Représente une commande passée par un utilisateur."""

    __tablename__ = "commandes"

    ALLOWED_STATUSES = {"en_attente", "validee", "expediee", "annulee"}

    id = db.Column(db.Integer, primary_key=True)
    utilisateur_id = db.Column(db.Integer, db.ForeignKey("utilisateurs.id"), nullable=False)
    statut = db.Column(db.String(20), nullable=False, default="en_attente")
    montant_total = db.Column(db.Float, nullable=False, default=0.0)
    adresse_livraison = db.Column(db.String(255), nullable=True)
    date_commande = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    utilisateur = db.relationship("Utilisateur", back_populates="commandes")
    lignes = db.relationship("LigneCommande", back_populates="commande", cascade="all, delete-orphan")

    def recalculate_total(self) -> float:
        """Recalcule et met à jour montant_total à partir des lignes de commande."""
        self.montant_total = sum(ligne.prix_unitaire * ligne.quantite for ligne in self.lignes)
        return self.montant_total

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "utilisateur_id": self.utilisateur_id,
            "statut": self.statut,
            "montant_total": self.montant_total,
            "adresse_livraison": self.adresse_livraison,
            "date_commande": self.date_commande.isoformat(),
            "lignes": [ligne.to_dict() for ligne in self.lignes],
        }


# Etape 3
class LigneCommande(db.Model):
    """Représente une ligne d'une commande (produit, quantité et prix unitaire)."""

    __tablename__ = "lignes_commande"

    id = db.Column(db.Integer, primary_key=True)
    commande_id = db.Column(db.Integer, db.ForeignKey("commandes.id"), nullable=False)
    produit_id = db.Column(db.Integer, db.ForeignKey("produits.id"), nullable=False)
    quantite = db.Column(db.Integer, nullable=False)
    prix_unitaire = db.Column(db.Float, nullable=False)

    commande = db.relationship("Commande", back_populates="lignes")
    produit = db.relationship("Produit", back_populates="lignes_commande")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "produit_id": self.produit_id,
            "nom_produit": self.produit.nom if self.produit else None,
            "quantite": self.quantite,
            "prix_unitaire": self.prix_unitaire,
            "total_ligne": self.quantite * self.prix_unitaire,
        }
