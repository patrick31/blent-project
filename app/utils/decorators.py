"""
Décorateurs Flask pour la protection des routes par authentification et rôle.

Réalisé pendant l'étape 1
"""
from functools import wraps

from flask import g, request

from ..extensions import db
from ..models import Utilisateur
from .helpers import decode_token, extract_bearer_token, json_error


# Etape 1
def token_required(func):
    """Vérifie la présence d'un token JWT valide dans l'en-tête Authorization."""

    @wraps(func)
    def wrapper(*args, **kwargs):
        """ Décorateur pour test d'un token JWT valide """
        token = extract_bearer_token(request.headers.get("Authorization"))
        if not token:
            return json_error("Token manquant ou format Bearer invalide.", 401)

        payload = decode_token(token)
        if not payload:
            return json_error("Token invalide ou expiré.", 401)

        utilisateur = db.session.get(Utilisateur, int(payload.get("sub")))
        if not utilisateur:
            return json_error("Utilisateur introuvable.", 401)

        g.current_user = utilisateur
        return func(*args, **kwargs)

    return wrapper
