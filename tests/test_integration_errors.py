import pytest
from app import create_app
from app.extensions import db


@pytest.fixture
def app():
    """Crée une application de test"""
    app = create_app()
    
    # ✅ Configuration pour les tests
    app.config['TESTING'] = True
    app.config['PROPAGATE_EXCEPTIONS'] = False  # Laisse les gestionnaires d'erreur fonctionner
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Crée un client de test"""
    return app.test_client()


class TestErrorPages:
    """Tests des pages d'erreur"""
    
    def test_404_error(self, client):
        """Test page 404 - Route inexistante"""
        response = client.get('/route-inexistante')
        assert response.status_code == 404
        assert b'404' in response.data
    
    def test_500_error(self, client):
        """Test page 500 - Exception serveur"""
        # ✅ Important : le gestionnaire d'erreur doit capturer l'exception
        response = client.get('/test/500')
        assert response.status_code == 500
        assert b'500' in response.data or b'Erreur serveur' in response.data
    
    def test_403_error(self, client):
        """Test page 403 - Accès refusé"""
        response = client.get('/test/403')
        assert response.status_code == 403
        assert b'403' in response.data
    
    def test_400_error(self, client):
        """Test page 400 - Requête invalide"""
        response = client.get('/test/400')
        assert response.status_code == 400
        assert b'400' in response.data
    
    def test_error_pages_have_home_button(self, client):
        """Vérifie que les pages d'erreur ont un bouton de retour"""
        response = client.get('/test/404')
        assert response.status_code == 404
        assert b'Retour' in response.data
    
    def test_error_pages_responsive(self, client):
        """Teste que les pages d'erreur s'affichent bien"""
        # ✅ Test tous les codes sans problème
        test_routes = [
            ('/test/404', 404),
            ('/test/403', 403),
            ('/test/400', 400),
            ('/test/500', 500),  # Maintenant ça doit marcher
        ]
        
        for route, expected_code in test_routes:
            response = client.get(route)
            assert response.status_code == expected_code, \
                f"Route {route} retourned {response.status_code}, attendu {expected_code}"
            assert len(response.data) > 100  # Contient du HTML