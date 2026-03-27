"""
Routes de gestion des commandes : création, consultation, lignes et mise à jour du statut.
Blueprint préfixé /api/commandes. Nécessite un token JWT valide.

Réalisé pendant l'étape 3 du projet
"""
from flask import Blueprint, g, request

from ..extensions import db
from ..models import Commande, LigneCommande, Produit
from ..utils.decorators import token_required
from ..utils.helpers import json_error, json_message

orders_bp = Blueprint("orders", __name__, url_prefix="/api/commandes")


# Etape 3
@orders_bp.post("")
@token_required
def create_order():
    """Crée une nouvelle commande pour l'utilisateur connecté à partir d'une liste de lignes."""
    data = request.get_json(silent=True) or {}
    lignes_data = data.get("lignes")
    adresse_livraison = (data.get("adresse_livraison") or "").strip() or None

    if not isinstance(lignes_data, list) or not lignes_data:
        return json_error("La commande doit contenir une liste non vide d'articles.", 400)

    commande = Commande(utilisateur_id=g.current_user.id, statut="en_attente", adresse_livraison=adresse_livraison)
    db.session.add(commande)

    for raw_ligne in lignes_data:
        produit_id = raw_ligne.get("produit_id")
        quantite = raw_ligne.get("quantite")

        try:
            produit_id = int(produit_id)
            quantite = int(quantite)
        except (TypeError, ValueError):
            return json_error("produit_id et quantite doivent être des entiers.", 400)

        if quantite <= 0:
            return json_error("La quantité doit être strictement positive.", 400)

        produit = db.session.get(Produit, produit_id)
        if not produit:
            return json_error(f"Produit {produit_id} introuvable.", 404)

        if produit.quantite_stock < quantite:
            return json_error(
                f"Stock insuffisant pour le produit {produit.nom}. Disponible: {produit.quantite_stock}.",
                400,
            )

        ligne = LigneCommande(
            commande=commande,
            produit=produit,
            quantite=quantite,
            prix_unitaire=produit.prix,
        )
        db.session.add(ligne)

    commande.recalculate_total()
    db.session.commit()
    return json_message("Commande créée.", 201, order=commande.to_dict())


# Etape 3
@orders_bp.get("")
@token_required
def list_orders():
    """Retourne toutes les commandes (admin) ou seulement celles de l'utilisateur connecté."""
    if g.current_user.role == "admin":
        commandes = Commande.query.order_by(Commande.id.asc()).all()
    else:
        commandes = Commande.query.filter_by(utilisateur_id=g.current_user.id).order_by(Commande.id.asc()).all()

    return json_message("Liste des commandes.", 200, orders=[c.to_dict() for c in commandes])


# Etape 3
@orders_bp.get("/<int:commande_id>")
@token_required
def get_order(commande_id: int):
    """Retourne le détail d'une commande (propriétaire ou admin uniquement)."""
    commande = db.session.get(Commande, commande_id)
    if not commande:
        return json_error("Commande introuvable.", 404)

    if g.current_user.role != "admin" and commande.utilisateur_id != g.current_user.id:
        return json_error("Accès interdit à cette commande.", 403)

    return json_message("Détail de la commande.", 200, order=commande.to_dict())


# Etape 3
@orders_bp.get("/<int:commande_id>/lignes")
@token_required
def get_order_lines(commande_id: int):
    """Retourne la liste des lignes d'une commande (propriétaire ou admin uniquement)."""
    commande = db.session.get(Commande, commande_id)
    if not commande:
        return json_error("Commande introuvable.", 404)

    if g.current_user.role != "admin" and commande.utilisateur_id != g.current_user.id:
        return json_error("Accès interdit à cette commande.", 403)

    return json_message("Lignes de la commande.", 200, lignes=[ligne.to_dict() for ligne in commande.lignes])


# Etape 3
@orders_bp.patch("/<int:commande_id>/status")
@token_required
def update_order_status(commande_id: int):
    """Met à jour le statut d'une commande et ajuste le stock si nécessaire (admin uniquement)."""
    if g.current_user.role != "admin":
        return json_error("Accès réservé aux administrateurs.", 403)

    commande = db.session.get(Commande, commande_id)
    if not commande:
        return json_error("Commande introuvable.", 404)

    data = request.get_json(silent=True) or {}
    new_statut = (data.get("status") or "").strip().lower()

    if new_statut not in Commande.ALLOWED_STATUSES:
        return json_error("Statut de commande invalide.", 400)

    # Seule la transition en_attente → validee décrémente le stock
    if commande.statut == "en_attente" and new_statut == "validee":
        for ligne in commande.lignes:
            if ligne.produit.quantite_stock < ligne.quantite:
                return json_error(
                    f"Stock insuffisant pour valider la commande sur {ligne.produit.nom}.",
                    400,
                )
        for ligne in commande.lignes:
            ligne.produit.quantite_stock -= ligne.quantite

    # Seule la transition validee → annulee restaure le stock
    if commande.statut == "validee" and new_statut == "annulee":
        for ligne in commande.lignes:
            ligne.produit.quantite_stock += ligne.quantite

    commande.statut = new_statut
    db.session.commit()
    return json_message("Statut de commande mis à jour.", 200, order=commande.to_dict())
