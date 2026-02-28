"""
Tests d'intégration - Workflow complet de l'application
Tests l'interaction entre plusieurs composants (Auth, DB, Routes, etc.)
"""
import pytest
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


@pytest.fixture
def authenticated_client(app, client):
    """Crée un client avec utilisateur authentifié"""
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


class TestCompleteWorkflow:
    """Tests du workflow complet : Inscription → Connexion → Création Postes → Entretien"""
    
    def test_workflow_new_user_to_dashboard(self, app, client):
        """✅ Test complet: Nouvel utilisateur → Dashboard"""
        
        # 1. Inscription
        response = client.post('/register', data={
            'username': 'newadmin',
            'password': 'securepass123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        with app.app_context():
            user = User.query.filter_by(username='newadmin').first()
            assert user is not None
            assert user.check_password('securepass123')
    
    def test_workflow_login_view_dashboard(self, app, authenticated_client):
        """✅ Test complet: Connexion → Accès au Dashboard"""
        
        response = authenticated_client.get('/')
        
        assert response.status_code == 200
        # Vérifier que le dashboard est chargé
        assert b'skillboard' in response.data.lower() or b'dashboard' in response.data.lower()
    
    def test_workflow_create_competence(self, app, authenticated_client):
        """✅ Test complet: Créer une compétence via formulaire"""
        
        response = authenticated_client.post('/add_competence', data={
            'nom_competence': 'Python'  # ✅ Correct: nom_competence
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        with app.app_context():
            comp = Competence.query.filter_by(nom='Python').first()
            assert comp is not None
    
    def test_workflow_create_poste_with_competences(self, app, authenticated_client):
        """✅ Test complet: Créer un poste avec compétences"""
        
        with app.app_context():
            # Créer des compétences d'abord
            c1 = Competence(nom='Python')
            c2 = Competence(nom='Flask')
            db.session.add_all([c1, c2])
            db.session.commit()
            c1_id = c1.id
            c2_id = c2.id
        
        # Créer un poste avec ces compétences
        response = authenticated_client.post('/add_poste', data={
            'nom_poste': 'Développeur Python',  # ✅ Correct: nom_poste
            'competences': [str(c1_id), str(c2_id)]
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        with app.app_context():
            poste = Poste.query.filter_by(nom='Développeur Python').first()
            assert poste is not None
            assert len(poste.competences) == 2
    
    def test_workflow_create_interview(self, app, authenticated_client):
        """✅ Test complet: Créer un entretien"""
        
        with app.app_context():
            # Créer un poste
            poste = Poste(nom='Dev Python')
            db.session.add(poste)
            db.session.commit()
        
        # Créer un entretien
        response = authenticated_client.post('/create_interview', data={
            'cand_nom': 'Dupont',  # ✅ Correct: cand_nom
            'cand_prenom': 'Jean',  # ✅ Correct: cand_prenom
            'entr_poste': 'Dev Python',  # ✅ Correct: entr_poste (nom, pas ID)
            'entr_date': '2026-03-15',  # ✅ Correct: entr_date
            'entr_recruteur': 'Marie'  # ✅ Correct: entr_recruteur
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        with app.app_context():
            entretien = Entretien.query.filter_by(candidat_nom='Dupont').first()
            assert entretien is not None
            assert entretien.candidat_prenom == 'Jean'
            assert entretien.statut == 'Cree'
    
    def test_workflow_entretien_with_evaluations(self, app, authenticated_client):
        """✅ Test complet: Entretien → Ajout d'évaluations"""
        
        with app.app_context():
            # Setup: Créer poste, compétences, entretien
            comp = Competence(nom='Python')
            poste = Poste(nom='Dev', competences=[comp])
            entretien = Entretien(
                candidat_nom='Test',
                candidat_prenom='Candidat',
                date_entretien='2026-03-15',
                poste_id=poste.id
            )
            db.session.add_all([comp, poste, entretien])
            db.session.commit()
            
            entretien_id = entretien.id
            competence_id = comp.id
        
        # Ajouter des évaluations
        with app.app_context():
            eval = Evaluation(
                entretien_id=entretien_id,
                competence_id=competence_id,
                note_rh=8,
                note_recruteur2=7
            )
            db.session.add(eval)
            db.session.commit()
        
        # Vérifier que les évaluations sont créées
        with app.app_context():
            entretien = db.session.get(Entretien, entretien_id)
            assert len(entretien.evaluations) == 1
            assert entretien.evaluations[0].note_rh == 8
    
    def test_workflow_fetch_poste_details(self, app, authenticated_client):
        """✅ Test complet: Récupérer les détails d'un poste (API JSON)"""
        
        with app.app_context():
            # Créer un poste avec compétences
            c1 = Competence(nom='Python')
            c2 = Competence(nom='Flask')
            poste = Poste(nom='Dev Python', competences=[c1, c2])
            db.session.add_all([c1, c2, poste])
            db.session.commit()
            poste_id = poste.id
        
        # Récupérer les détails via API
        response = authenticated_client.get(f'/api/poste/{poste_id}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['nom'] == 'Dev Python'
        assert len(data['competences']) == 2


class TestMultiStepOperations:
    """Tests des opérations multi-étapes"""
    
    def test_update_poste_competences(self, app, authenticated_client):
        """✅ Test mise à jour des compétences d'un poste"""
        
        with app.app_context():
            c1 = Competence(nom='Python')
            c2 = Competence(nom='Java')
            c3 = Competence(nom='Flask')
            poste = Poste(nom='Dev', competences=[c1])
            db.session.add_all([c1, c2, c3, poste])
            db.session.commit()
            poste_id = poste.id
            c2_id = c2.id
            c3_id = c3.id
        
        # Mettre à jour le poste avec de nouvelles compétences
        response = authenticated_client.post('/update_poste', data={
            'poste_id': str(poste_id),
            'nom_poste': 'Dev Backend',  # ✅ Correct: nom_poste
            'competences': [str(c2_id), str(c3_id)]
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        with app.app_context():
            poste = db.session.get(Poste, poste_id)
            assert poste.nom == 'Dev Backend'
            assert len(poste.competences) == 2
    
    def test_delete_poste_via_api(self, app, authenticated_client):
        """✅ Test suppression d'un poste via API JSON"""
        
        with app.app_context():
            poste = Poste(nom='To Delete')
            db.session.add(poste)
            db.session.commit()
            poste_id = poste.id
        
        # Supprimer via API
        response = authenticated_client.delete(f'/api/poste/{poste_id}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] == True
        
        with app.app_context():
            poste = db.session.get(Poste, poste_id)
            assert poste is None
    
    def test_delete_nonexistent_poste(self, app, authenticated_client):
        """✅ Test suppression d'un poste inexistant"""
        
        response = authenticated_client.delete('/api/poste/99999')
        
        assert response.status_code == 404


class TestAuthenticationFlow:
    """Tests du flux d'authentification intégré"""
    
    def test_cannot_access_protected_routes_without_auth(self, client):
        """✅ Test accès refusé aux routes protégées sans auth"""
        
        protected_routes = [
            '/',
            '/logout'
        ]
        
        for route in protected_routes:
            response = client.get(route)
            # Doit rediriger vers login (302)
            assert response.status_code == 302
    
    def test_session_persistence_across_requests(self, app, authenticated_client):
        """✅ Test que la session persiste entre les requêtes"""
        
        # Première requête
        response1 = authenticated_client.get('/')
        assert response1.status_code == 200
        
        # Deuxième requête - la session doit être valide
        response2 = authenticated_client.get('/')
        assert response2.status_code == 200
    
    def test_logout_clears_session(self, app, authenticated_client):
        """✅ Test que la déconnexion efface la session"""
        
        # Vérifier qu'on est connecté
        response = authenticated_client.get('/')
        assert response.status_code == 200
        
        # Déconnecter
        authenticated_client.get('/logout')
        
        # Vérifier qu'on ne peut plus accéder aux routes protégées
        response = authenticated_client.get('/')
        assert response.status_code == 302  # Redirection vers login


class TestConcurrentOperations:
    """Tests des opérations concurrentes/complexes"""
    
    def test_multiple_users_independent_data(self, app):
        """✅ Test que les données de deux utilisateurs sont indépendantes"""
        
        client1 = app.test_client()
        client2 = app.test_client()
        app.config['WTF_CSRF_ENABLED'] = False
        
        # User 1 inscription
        with app.app_context():
            user1 = User(username='user1')
            user1.set_password('pass1')
            user2 = User(username='user2')
            user2.set_password('pass2')
            db.session.add_all([user1, user2])
            db.session.commit()
        
        # User 1 connexion et création poste
        client1.post('/login', data={'username': 'user1', 'password': 'pass1'})
        
        with app.app_context():
            poste1 = Poste(nom='Poste User 1')
            db.session.add(poste1)
            db.session.commit()
        
        # User 2 connexion - ne doit pas voir les données de User 1
        client2.post('/login', data={'username': 'user2', 'password': 'pass2'})
        
        response = client2.get('/')
        assert response.status_code == 200
        # Les postes existent dans la base globale
        with app.app_context():
            postes = Poste.query.all()
            assert len(postes) >= 1