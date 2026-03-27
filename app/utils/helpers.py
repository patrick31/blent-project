"""
Fonctions utilitaires partagées : réponses JSON standardisées et gestion des tokens JWT.

Réalisé pendant la préparation du projet (étape 0) et extension à l'étape 1 du projet
"""
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import jwt
from flask import jsonify, current_app


# Etape 0
def json_error(message: str, status_code: int):
    """Retourne une réponse JSON d'erreur avec le message et le code HTTP fournis."""
    response = jsonify({"error": message})
    response.status_code = status_code
    return response


# Etape 0
def json_message(message: str, status_code: int = 200, **kwargs: Any):
    """Retourne une réponse JSON de succès avec le message et les données supplémentaires."""
    payload = {"message": message}
    payload.update(kwargs)
    response = jsonify(payload)
    response.status_code = status_code
    return response


# Etape 1
def generate_token(user) -> str:
    """Génère un token JWT signé pour l'utilisateur, valable 24 heures.

    Args:
        user: Instance utilisateur avec les attributs id, nom et role.

    Returns:
        Token JWT encodé sous forme de chaîne.
    """
    payload = {
        "sub": str(user.id),
        "nom": user.nom,
        "role": user.role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=24),
    }
    # Remarques :
    #   — exp est un claim officiel de JWT et sera automatiquement traité par jwt.decode avec expiration
    #   — sub est aussi un claim officiel pour l'identifiant du sujet mais pas vérifié automatiquement par JWT
    #   — role et nom sont spécifiques à cette API
    return jwt.encode(payload, current_app.config["JWT_SECRET_KEY"], algorithm="HS256")


# Etape 1
def decode_token(token: str) -> Optional[dict]:
    """Décode et valide un token JWT.

    Args:
        token: Token JWT à décoder.

    Returns:
        Dictionnaire contenant le payload du token, ou None si le token est
        expiré ou invalide.
    """
    try:
        return jwt.decode(token, current_app.config["JWT_SECRET_KEY"], algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


# Etape 1
def extract_bearer_token(auth_header: Optional[str]) -> Optional[str]:
    """Extrait le token Bearer depuis un en-tête Authorization.

    Args:
        auth_header: Valeur de l'en-tête Authorization (ex: "Bearer <token>").

    Returns:
        Le token brut si l'en-tête est valide, None sinon.
    """
    if not auth_header:
        return None

    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    return parts[1]
