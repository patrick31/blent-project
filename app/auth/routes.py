"""
Routes d'authentification : inscription, connexion et consultation du profil.
Blueprint préfixé /api/auth.

Réalisé pendant l'étape 1 du projet
"""
from flask import Blueprint, g, request
from sqlalchemy import or_
from ..extensions import db
from ..models import Utilisateur
from ..utils.decorators import token_required
from ..utils.helpers import generate_token, json_error, json_message

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


# Etape 1
@auth_bp.post("/register")
def register():
    """Crée un nouveau compte utilisateur avec le rôle client."""
    data = request.get_json(silent=True) or {}

    nom = (data.get("nom") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not nom or not email or not password:
        return json_error("nom, email et password sont obligatoires.", 400)

    existing = Utilisateur.query.filter(or_(Utilisateur.nom == nom, Utilisateur.email == email)).first()
    if existing:
        return json_error("Un utilisateur existe déjà avec ce nom ou cet email.", 409)

    utilisateur = Utilisateur(nom=nom, email=email, role="client")
    utilisateur.set_password(password)
    db.session.add(utilisateur)
    db.session.commit()

    return json_message("Utilisateur créé.", 201, user=utilisateur.to_dict())


# Etape 1
@auth_bp.post("/login")
def login():
    """Authentifie un utilisateur par email ou nom et retourne un token JWT."""
    data = request.get_json(silent=True) or {}
    identifiant = (data.get("email") or data.get("nom") or "").strip()
    password = data.get("password") or ""

    if not identifiant or not password:
        return json_error("email (ou nom) et password sont obligatoires.", 400)

    utilisateur = Utilisateur.query.filter(
        or_(Utilisateur.email == identifiant.lower(), Utilisateur.nom == identifiant)
    ).first()
    if not utilisateur or not utilisateur.check_password(password):
        return json_error("Identifiants invalides.", 401)

    token = generate_token(utilisateur)
    return json_message("Connexion réussie.", 200, token=token, user=utilisateur.to_dict())


# Etape 1
@auth_bp.get("/me")
@token_required
def me():
    """Retourne le profil de l'utilisateur actuellement connecté."""
    return json_message("Profil utilisateur.", 200, user=g.current_user.to_dict())
