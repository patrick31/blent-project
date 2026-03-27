"""
Routes du catalogue produits : liste, détail, création, modification et suppression.
Blueprint préfixé /api/produits. Les écritures sont réservées aux administrateurs.

Réalisé pendant l'étape 2 du projet
"""

from flask import Blueprint, request
from sqlalchemy import or_

from ..extensions import db
from ..models import Produit
from ..utils.decorators import admin_required
from ..utils.helpers import json_error, json_message

products_bp = Blueprint("products", __name__, url_prefix="/api/produits")


# Etape 2
@products_bp.get("")
def list_products():
    """Retourne la liste des produits avec filtres optionnels ?trouve= et ?categorie=."""
    trouve = (request.args.get("trouve") or "").strip()
    categorie = (request.args.get("categorie") or "").strip()

    query = Produit.query

    if trouve:
        term = f"%{trouve}%"
        query = query.filter(or_(Produit.nom.ilike(term), Produit.description.ilike(term)))

    if categorie:
        query = query.filter(Produit.categorie.ilike(f"%{categorie}%"))

    produits = query.order_by(Produit.id.asc()).all()
    return json_message("Liste des produits.", 200, products=[p.to_dict() for p in produits])


# Etape 2
@products_bp.get("/<int:produit_id>")
def get_product(produit_id: int):
    """Retourne le détail d'un produit par son identifiant."""
    produit = db.session.get(Produit, produit_id)
    if not produit:
        return json_error("Produit introuvable.", 404)
    return json_message("Détail du produit.", 200, product=produit.to_dict())


# Etape 2
@products_bp.post("")
@admin_required
def create_product():
    """Crée un nouveau produit dans le catalogue (admin uniquement)."""
    data = request.get_json(silent=True) or {}

    nom = (data.get("nom") or "").strip()
    description = (data.get("description") or "").strip() or None
    categorie = (data.get("categorie") or "").strip() or None
    prix = data.get("prix")
    quantite_stock = data.get("quantite_stock", 0)

    if not nom:
        return json_error("Le nom du produit est obligatoire.", 400)

    if prix is None:
        return json_error("Le prix est obligatoire.", 400)

    try:
        prix = float(prix)
        quantite_stock = int(quantite_stock)
    except (TypeError, ValueError):
        return json_error("Le prix doit être un nombre et le stock un entier.", 400)

    if prix < 0 or quantite_stock < 0:
        return json_error("Le prix et le stock doivent être positifs ou nuls.", 400)

    produit = Produit(
        nom=nom,
        description=description,
        categorie=categorie,
        prix=prix,
        quantite_stock=quantite_stock,
    )
    db.session.add(produit)
    db.session.commit()

    return json_message("Produit créé.", 201, product=produit.to_dict())


# Etape 2
@products_bp.put("/<int:produit_id>")
@admin_required
def update_product(produit_id: int):
    """Met à jour les champs d'un produit existant (admin uniquement)."""
    produit = db.session.get(Produit, produit_id)
    if not produit:
        return json_error("Produit introuvable.", 404)

    data = request.get_json(silent=True) or {}

    if "nom" in data:
        produit.nom = (data.get("nom") or "").strip()
        if not produit.nom:
            return json_error("Le nom du produit ne peut pas être vide.", 400)

    if "description" in data:
        produit.description = (data.get("description") or "").strip() or None

    if "categorie" in data:
        produit.categorie = (data.get("categorie") or "").strip() or None

    if "prix" in data:
        try:
            produit.prix = float(data.get("prix"))
        except (TypeError, ValueError):
            return json_error("Le prix doit être un nombre.", 400)
        if produit.prix < 0:
            return json_error("Le prix doit être positif ou nul.", 400)

    if "quantite_stock" in data:
        try:
            produit.quantite_stock = int(data.get("quantite_stock"))
        except (TypeError, ValueError):
            return json_error("Le stock doit être un entier.", 400)
        if produit.quantite_stock < 0:
            return json_error("Le stock doit être positif ou nul.", 400)

    db.session.commit()
    return json_message("Produit mis à jour.", 200, product=produit.to_dict())


# Etape 2
@products_bp.delete("/<int:produit_id>")
@admin_required
def delete_product(produit_id: int):
    """Supprime un produit du catalogue (admin uniquement)."""
    produit = db.session.get(Produit, produit_id)
    if not produit:
        return json_error("Produit introuvable.", 404)

    db.session.delete(produit)
    db.session.commit()
    return json_message("Produit supprimé.", 200)
