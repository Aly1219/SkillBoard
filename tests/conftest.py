"""
Configuration et fixtures partagées pour tous les tests
"""
import pytest
import os
from app import create_app
from app.extensions import db
from app.models import User, Competence, Poste


@pytest.fixture(scope='function')
def app():
    """
    Crée une application Flask de test avec base de données en mémoire
    """
    app = create_app()
    app.config['TESTING'] = True
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