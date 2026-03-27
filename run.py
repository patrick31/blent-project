"""
Point d'entrée alternatif pour lancer le serveur Flask en développement.
Préférer la commande : flask run  (via .flaskenv)
"""
from app import __version__, create_app
from app.config import DevelopmentConfig

app = create_app(DevelopmentConfig)

if __name__ == "__main__":
    print(f"DigiMarket v{__version__} — http://localhost:5001")
    app.run(debug=True, port=5001)
