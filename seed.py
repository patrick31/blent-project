"""
Script d'initialisation de la base de données démo avec des données de test.
Usage : python seed.py
"""
from app import create_app
from app.config import DevelopmentConfig, INSTANCE_DIR
from app.extensions import db
from app.models import Commande, LigneCommande, Produit, Utilisateur

INSTANCE_DIR.mkdir(exist_ok=True)
app = create_app(DevelopmentConfig, skip_db_check=True)

with app.app_context():
    db.drop_all()
    db.create_all()

    # Utilisateurs
    admin = Utilisateur(nom="admin", email="admin@digimarket.com", role="admin")
    admin.set_password("admin1234")

    alice = Utilisateur(nom="alice", email="alice@example.com", role="client")
    alice.set_password("alice1234")

    bob = Utilisateur(nom="bob", email="bob@example.com", role="client")
    bob.set_password("bob1234")

    db.session.add_all([admin, alice, bob])
    db.session.commit()

    # Produits
    produits = [
        Produit(nom="Laptop Pro 15", description="Ordinateur portable haute performance, 16Go RAM, 512Go SSD", prix=1499.99, quantite_stock=10, categorie="ordinateur portable"),
        Produit(nom="Gaming Mouse X200", description="Souris gaming 16000 DPI, RGB, 7 boutons programmables", prix=59.90, quantite_stock=50, categorie="peripherique gaming"),
        Produit(nom="USB-C Dock Pro", description="Station d'accueil 12-en-1, 4K HDMI, 100W PD", prix=129.00, quantite_stock=25, categorie="accessoire"),
        Produit(nom="Clavier Mécanique TKL", description="Clavier sans pavé numérique, switchs Cherry MX Red", prix=89.99, quantite_stock=30, categorie="peripherique"),
        Produit(nom='Écran 27" 4K', description="Moniteur IPS 4K UHD, 144Hz, HDR400", prix=449.00, quantite_stock=8, categorie="ecran"),
        Produit(nom="SSD NVMe 1To", description="Disque SSD M.2 NVMe, lecture 3500 Mo/s", prix=99.00, quantite_stock=40, categorie="stockage"),
        Produit(nom="Webcam HD 1080p", description="Caméra USB Full HD avec micro intégré", prix=49.90, quantite_stock=15, categorie="peripherique"),
        Produit(nom="Casque Gamer 7.1", description="Casque surround virtuel 7.1 avec micro rétractable", prix=79.99, quantite_stock=20, categorie="peripherique gaming"),
    ]
    db.session.add_all(produits)
    db.session.commit()

    # Commandes
    commande1 = Commande(
        utilisateur_id=alice.id,
        statut="validee",
        adresse_livraison="10 rue des Lilas, 75011 Paris",
    )
    db.session.add(commande1)
    db.session.flush()

    ligne1 = LigneCommande(commande_id=commande1.id, produit_id=produits[0].id, quantite=1, prix_unitaire=produits[0].prix)
    ligne2 = LigneCommande(commande_id=commande1.id, produit_id=produits[1].id, quantite=2, prix_unitaire=produits[1].prix)
    db.session.add_all([ligne1, ligne2])
    commande1.recalculate_total()
    produits[0].quantite_stock -= 1
    produits[1].quantite_stock -= 2

    commande2 = Commande(
        utilisateur_id=bob.id,
        statut="en_attente",
        adresse_livraison="5 avenue Victor Hugo, 69002 Lyon",
    )
    db.session.add(commande2)
    db.session.flush()

    ligne3 = LigneCommande(commande_id=commande2.id, produit_id=produits[2].id, quantite=1, prix_unitaire=produits[2].prix)
    ligne4 = LigneCommande(commande_id=commande2.id, produit_id=produits[5].id, quantite=2, prix_unitaire=produits[5].prix)
    db.session.add_all([ligne3, ligne4])
    commande2.recalculate_total()

    db.session.commit()

    print("Base de données initialisée avec succès.")
    print(f"  {Utilisateur.query.count()} utilisateurs créés")
    print(f"  {Produit.query.count()} produits créés")
    print(f"  {Commande.query.count()} commandes créées")
    print()
    print("Comptes disponibles :")
    print("  admin@digimarket.com / admin1234  (rôle: admin)")
    print("  alice@example.com / alice1234     (rôle: client)")
    print("  bob@example.com / bob1234         (rôle: client)")
