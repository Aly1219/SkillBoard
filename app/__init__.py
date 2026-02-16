from flask import Flask
from app.utils import resource_path
from app.extensions import db, login_manager
from config import Config
from app.models import User


def create_app():
    # Définition des dossiers templates et static avec resource_path
    template_dir = resource_path("templates")
    static_dir = resource_path("static")
    
    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
    app.config.from_object(Config)

    # Initialisation des extensions
    db.init_app(app)

    # --- Config Flask Login ---
    login_manager.init_app(app)
    login_manager.login_view = 'main.login' # Redirection si utilisateur non connecté
    login_manager.login_message = "Veuillez vous connecter pour accéder à cette page"

    # Enregistrement des Blueprints (les routes)
    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    with app.app_context():
        db.create_all()
        init_db(app)
    return app

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def init_db(app):
    """Logique d'initialisation de la base de données"""
    from app.models import Poste, Competence
    
    if not Poste.query.first():
        print("Base vide détectée, insertion des données de test...")
        c1 = Competence(nom="Français écrit")
        c2 = Competence(nom="Français parlé")
        c3 = Competence(nom="Excel")
        p1 = Poste(nom="Secrétaire", competences=[c1, c2])
        
        db.session.add_all([c1, c2, c3, p1])
        db.session.commit()
        print("Données insérées !")