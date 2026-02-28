"""
Tests unitaires pour l'authentification
"""
import pytest
from app import create_app
from app.extensions import db
from app.models import User


@pytest.fixture
def app():
    """Crée une application de test"""
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
    """Crée un client de test"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Crée un test runner CLI"""
    return app.test_cli_runner()


class TestAuthRoutes:
    """Tests pour les routes d'authentification"""
    
    def test_register_page_loads(self, client):
        """✅ Test que la page d'inscription se charge"""
        response = client.get('/register')
        assert response.status_code == 200
        assert b'register' in response.data.lower() or b'inscription' in response.data.lower()
    
    def test_register_new_user(self, app, client):
        """✅ Test l'inscription d'un nouvel utilisateur"""
        with app.app_context():
            # Aucun utilisateur existant
            response = client.post('/register', data={
                'username': 'newuser',
                'password': 'securepass123'
            }, follow_redirects=True)
            
            assert response.status_code == 200
            user = User.query.filter_by(username='newuser').first()
            assert user is not None
            assert user.check_password('securepass123')
    
    def test_login_page_loads(self, app, client):
        """✅ Test que la page de connexion se charge"""
        with app.app_context():
            # Créer un utilisateur pour que login soit accessible
            user = User(username='testuser')
            user.set_password('password')
            db.session.add(user)
            db.session.commit()
        
        response = client.get('/login')
        assert response.status_code == 200
    
    def test_login_valid_credentials(self, app, client):
        """✅ Test la connexion avec les bonnes identifiants"""
        with app.app_context():
            user = User(username='testuser')
            user.set_password('correctpass')
            db.session.add(user)
            db.session.commit()
        
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'correctpass'
        }, follow_redirects=True)
        
        # Vérifier qu'on est redirigé vers le home (connexion réussie)
        assert response.status_code == 200
        # Le dashboard doit contenir certains éléments (adapter selon votre template)
        assert b'dashboard' in response.data.lower() or b'entretien' in response.data.lower()
    
    def test_login_invalid_password(self, app, client):
        """✅ Test la connexion avec un mauvais mot de passe"""
        with app.app_context():
            user = User(username='testuser')
            user.set_password('correctpass')
            db.session.add(user)
            db.session.commit()
        
        # Faire la requête sans follow_redirects pour capturer les flash messages
        response = client.post('/login', data={
            'username': 'testuser',
            'password': 'wrongpass'
        })
        
        # La réponse doit être un retour à la page login (pas de redirection)
        assert response.status_code == 200
        # Vérifier que le formulaire de login est toujours affiché
        assert b'se connecter' in response.data.lower() or b'connecter' in response.data.lower()
    
    def test_login_nonexistent_user(self, app, client):
        """✅ Test la connexion avec un user inexistant"""
        with app.app_context():
            user = User(username='testuser')
            user.set_password('pass')
            db.session.add(user)
            db.session.commit()
        
        response = client.post('/login', data={
            'username': 'nonexistent',
            'password': 'anypass'
        })
        
        # Doit rester sur la page login
        assert response.status_code == 200
        # Vérifier que le formulaire est présent
        assert b'se connecter' in response.data.lower()
    
    def test_logout(self, app, client):
        """✅ Test la déconnexion"""
        with app.app_context():
            user = User(username='testuser')
            user.set_password('pass')
            db.session.add(user)
            db.session.commit()
        
        # Connexion
        client.post('/login', data={
            'username': 'testuser',
            'password': 'pass'
        }, follow_redirects=True)
        
        # Déconnexion
        response = client.get('/logout', follow_redirects=True)
        assert response.status_code == 200
    
    def test_protected_route_requires_login(self, client):
        """✅ Test qu'une route protégée demande la connexion"""
        response = client.get('/')
        # Doit rediriger vers login (302)
        assert response.status_code == 302
        assert b'login' in response.data or response.location.endswith('/login')
    
    def test_already_authenticated_redirect_to_home(self, app, client):
        """✅ Test que l'utilisateur connecté est redirigé au home depuis login"""
        with app.app_context():
            user = User(username='testuser')
            user.set_password('pass')
            db.session.add(user)
            db.session.commit()
        
        # Connexion
        client.post('/login', data={
            'username': 'testuser',
            'password': 'pass'
        })
        
        # Essayer d'accéder à /login quand déjà connecté
        response = client.get('/login')
        # Doit rediriger vers home
        assert response.status_code == 302