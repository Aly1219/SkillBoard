"""
Configuration et fixtures partagées pour tous les tests.
Chargé automatiquement par pytest — aucun import nécessaire dans les fichiers de test.
"""
import pytest
from datetime import date
from app import create_app
from app.extensions import db
from app.models import User, Competence, Poste


# ============================================================
# FIXTURE DE BASE — application et client
# ============================================================

@pytest.fixture(scope='function')
def app():
    """
    Crée une application Flask de test isolée avec base SQLite en mémoire.
    ENV n'est pas 'development' → init_db() ne s'exécute pas, base propre à chaque test.
    """
    app = create_app()
    app.config['TESTING'] = True
    app.config['ENV'] = 'testing'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False

    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Crée un client de test Flask"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Crée un test runner CLI"""
    return app.test_cli_runner()


# ============================================================
# FIXTURE CLIENT AUTHENTIFIÉ — partagée dans tous les fichiers
# ============================================================

@pytest.fixture
def authenticated_client(app, client):
    """
    Crée un client avec un utilisateur déjà connecté.
    Utilisable dans tous les tests d'intégration.
    """
    with app.app_context():
        user = User(username='admin')
        user.set_password('admin123')
        db.session.add(user)
        db.session.commit()

    client.post('/login', data={
        'username': 'admin',
        'password': 'admin123'
    })
    return client


# ============================================================
# FACTORIES — création d'objets de test réutilisables
# ============================================================

@pytest.fixture
def user_factory(app):
    """Factory pour créer des utilisateurs de test"""
    def _create_user(username='testuser', password='testpass123'):
        with app.app_context():
            user = User(username=username)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            return user
    return _create_user


@pytest.fixture
def competence_factory(app):
    """Factory pour créer des compétences de test"""
    def _create_competence(nom='Python'):
        with app.app_context():
            comp = Competence(nom=nom)
            db.session.add(comp)
            db.session.commit()
            return comp
    return _create_competence


@pytest.fixture
def poste_factory(app):
    """Factory pour créer des postes de test"""
    def _create_poste(nom='Développeur', competences=None):
        with app.app_context():
            poste = Poste(nom=nom, competences=competences or [])
            db.session.add(poste)
            db.session.commit()
            return poste
    return _create_poste