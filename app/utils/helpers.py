"""
Fonctions utilitaires partagées : réponses JSON standardisées et gestion des tokens JWT.

Réalisé pendant la préparation du projet (étape 0)
"""
from typing import Any

from flask import jsonify


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
