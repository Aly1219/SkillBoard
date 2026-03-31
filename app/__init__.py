"""
Initialisation de l'application Flask — Application Factory pattern
"""
import logging
from flask import Flask, render_template
from flask_migrate import Migrate
from app.extensions import db, login_manager, cache
from app.models import User
from app.utils import resource_path
from config import Config

# ============================================================
# TABLE DES MATIÈRES
# 1.  FACTORY              create_app()
# 2.  USER LOADER          load_user()
# 3.  GESTIONNAIRES D'ERREUR  register_error_handlers()
# 4.  INITIALISATION DB    init_db()
# ============================================================


# ============================================================
# 1. FACTORY
# ============================================================
def create_app():
    template_dir = resource_path("templates")
    static_dir   = resource_path("static")

    app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)

    # --- Configuration ---
    app.config.from_object(Config)

    # --- Extensions ---
    db.init_app(app)
    cache.init_app(app)
    Migrate(app, db)

    # --- Flask-Login ---
    login_manager.init_app(app)
    login_manager.login_view = 'main.login'

    with app.app_context():
        db.create_all()

        # Blueprint principal (routes web)
        from app.routes import bp as main_bp
        app.register_blueprint(main_bp)

        # Blueprint API REST (optionnel)
        try:
            from app.api import api_bp
            app.register_blueprint(api_bp)
            app.logger.info("API REST chargée avec succès")
        except ImportError as e:
            app.logger.warning(f"Impossible de charger l'API : {e}")

    register_error_handlers(app)

    return app


# ============================================================
# 2. USER LOADER
# ============================================================
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# ============================================================
# 3. GESTIONNAIRES D'ERREUR
# ============================================================
def register_error_handlers(app):
    """Enregistre les pages d'erreur personnalisées"""

    @app.errorhandler(400)
    def bad_request_error(error):
        return render_template('error_400.html'), 400

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template('error_403.html'), 403

    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('error_404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('error_500.html'), 500


# ============================================================
# 4. INITIALISATION DB (dev uniquement)
# ============================================================
def init_db(app):
    """Insère des données de test si la base est vide"""
    from app.models import Poste, Competence

    if not Poste.query.first():
        app.logger.info("Base vide détectée — insertion des données de test...")

        c1 = Competence(nom="Français écrit")
        c2 = Competence(nom="Français parlé")
        c3 = Competence(nom="Excel")
        p1 = Poste(nom="Secrétaire", competences=[c1, c2])

        db.session.add_all([c1, c2, c3, p1])
        db.session.commit()

        app.logger.info("Données de test insérées avec succès")