"""
Tests unitaires pour l'authentification.
"""
import pytest
from app.extensions import db
from app.models import User


# Fixtures app et client supprimées — définies dans conftest.py


class TestAuthRoutes:
    """Tests pour les routes d'authentification"""

    def test_register_page_loads(self, client):
        """La page d'inscription se charge"""
        response = client.get('/register')
        assert response.status_code == 200

    def test_register_new_user(self, app, client):
        """Inscription d'un nouvel utilisateur"""
        response = client.post('/register', data={
            'username': 'newuser',
            'password': 'securepass123'
        }, follow_redirects=True)

        assert response.status_code == 200
        with app.app_context():
            user = User.query.filter_by(username='newuser').first()
            assert user is not None
            assert user.check_password('securepass123')

    def test_login_page_loads(self, app, client):
        """La page de connexion se charge si un utilisateur existe"""
        with app.app_context():
            user = User(username='testuser')
            user.set_password('password')
            db.session.add(user)
            db.session.commit()

        response = client.get('/login')
        assert response.status_code == 200

    def test_login_valid_credentials(self, app, client):
        """Connexion réussie avec les bons identifiants"""
        with app.app_context():
            user = User(username='testuser')
            user.set_password('correctpass')
            db.session.add(user)
            db.session.commit()

        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'correctpass'
        }, follow_redirects=True)

        assert response.status_code == 200
        assert b'dashboard' in response.data.lower() or b'entretien' in response.data.lower()

    def test_login_invalid_password(self, app, client):
        """Connexion échouée avec un mauvais mot de passe"""
        with app.app_context():
            user = User(username='testuser')
            user.set_password('correctpass')
            db.session.add(user)
            db.session.commit()

        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'wrongpass'
        })

        assert response.status_code == 200
        assert b'connecter' in response.data.lower()

    def test_login_nonexistent_user(self, app, client):
        """Connexion échouée avec un utilisateur inexistant"""
        with app.app_context():
            user = User(username='testuser')
            user.set_password('pass')
            db.session.add(user)
            db.session.commit()

        response = client.post('/login', data={
            'username': 'nonexistent',
            'password': 'anypass'
        })

        assert response.status_code == 200
        assert b'connecter' in response.data.lower()

    def test_logout(self, app, client):
        """La déconnexion fonctionne"""
        with app.app_context():
            user = User(username='testuser')
            user.set_password('pass')
            db.session.add(user)
            db.session.commit()

        client.post('/login', data={'username': 'testuser', 'password': 'pass'})
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200

    def test_protected_route_requires_login(self, client):
        """Une route protégée redirige vers login si non connecté"""
        response = client.get('/')
        assert response.status_code == 302
        assert b'login' in response.data or 'login' in response.location

    def test_already_authenticated_redirect_to_home(self, app, client):
        """Un utilisateur connecté est redirigé depuis /login vers le dashboard"""
        with app.app_context():
            user = User(username='testuser')
            user.set_password('pass')
            db.session.add(user)
            db.session.commit()

        client.post('/login', data={'username': 'testuser', 'password': 'pass'})
        response = client.get('/login')
        assert response.status_code == 302