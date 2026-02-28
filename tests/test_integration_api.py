"""
Tests d'intégration - API REST avec Swagger
Teste l'API REST avec Flask-RESTX
⚠️ ATTENTION: L'API REST n'est PAS encore implémentée pour tous les endpoints
Cette suite teste ce qui est disponible
"""
import pytest
import json
from app import create_app
from app.extensions import db
from app.models import User, Competence, Poste, Entretien, Evaluation


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


class TestAPICompetencesBasic:
    """Tests basiques des endpoints compétences API"""
    
    def test_get_competence_by_id(self, app, client):
        """✅ Test récupération d'une compétence par ID"""
        
        with app.app_context():
            comp = Competence(nom='Python')
            db.session.add(comp)
            db.session.commit()
            comp_id = comp.id
        
        response = client.get(f'/api/v1/competences/{comp_id}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['nom'] == 'Python'
    
    def test_update_competence_via_api(self, app, client):
        """✅ Test mise à jour d'une compétence"""
        
        with app.app_context():
            comp = Competence(nom='OldName')
            db.session.add(comp)
            db.session.commit()
            comp_id = comp.id
        
        response = client.put(f'/api/v1/competences/{comp_id}',
            json={'nom': 'NewName'},
            content_type='application/json'
        )
        
        assert response.status_code == 200
        
        with app.app_context():
            comp = db.session.get(Competence, comp_id)
            assert comp.nom == 'NewName'
    
    def test_delete_competence_via_api(self, app, client):
        """✅ Test suppression d'une compétence"""
        
        with app.app_context():
            comp = Competence(nom='ToDelete')
            db.session.add(comp)
            db.session.commit()
            comp_id = comp.id
        
        response = client.delete(f'/api/v1/competences/{comp_id}')
        
        # ✅ Peut retourner 200 ou 204 (No Content) - les deux sont valides
        assert response.status_code in [200, 204]
        
        with app.app_context():
            comp = db.session.get(Competence, comp_id)
            assert comp is None


class TestAPIAuth:
    """Tests de l'API d'authentification"""
    
    def test_register_via_api(self, app, client):
        """✅ Test inscription via API"""
        
        response = client.post('/api/v1/auth/register',
            json={
                'username': 'apiuser',
                'password': 'apipass123'
            },
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] == True
        assert data['username'] == 'apiuser'
    
    def test_login_via_api(self, app, client):
        """✅ Test connexion via API"""
        
        with app.app_context():
            user = User(username='apiuser')
            user.set_password('apipass')
            db.session.add(user)
            db.session.commit()
        
        response = client.post('/api/v1/auth/login',
            json={
                'username': 'apiuser',
                'password': 'apipass'
            },
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
    
    def test_login_invalid_credentials_via_api(self, app, client):
        """✅ Test connexion avec mauvais identifiants via API"""
        
        with app.app_context():
            user = User(username='apiuser')
            user.set_password('correct')
            db.session.add(user)
            db.session.commit()
        
        response = client.post('/api/v1/auth/login',
            json={
                'username': 'apiuser',
                'password': 'wrong'
            },
            content_type='application/json'
        )
        
        assert response.status_code == 401
        data = response.get_json()
        assert data['success'] == False


class TestAPIErrors:
    """Tests de gestion d'erreurs de l'API"""
    
    def test_get_nonexistent_competence(self, client):
        """✅ Test récupération d'une compétence inexistante"""
        
        response = client.get('/api/v1/competences/99999')
        
        assert response.status_code == 404
    
    def test_api_documentation_accessible(self, client):
        """✅ Test que la documentation Swagger est accessible"""
        
        response = client.get('/api/v1/docs')
        
        assert response.status_code == 200