"""
Tests d'intégration — Workflow complet de l'application.
Teste l'interaction entre plusieurs composants (Auth, DB, Routes).
"""
import pytest
from datetime import date
from sqlalchemy import select
from app.extensions import db
from app.models import User, Competence, Poste, Entretien, Evaluation


# Fixtures app, client et authenticated_client supprimées — définies dans conftest.py


class TestCompleteWorkflow:
    """Workflow complet : Inscription → Connexion → Postes → Entretien"""

    def test_workflow_new_user_to_dashboard(self, app, client):
        """Nouvel utilisateur → inscription → dashboard"""
        response = client.post('/register', data={
            'username': 'newadmin',
            'password': 'securepass123'
        }, follow_redirects=True)

        assert response.status_code == 200
        with app.app_context():
            user = db.session.scalars(select(User).where(User.username == 'newadmin')).first()
            assert user is not None
            assert user.check_password('securepass123')

    def test_workflow_login_view_dashboard(self, authenticated_client):
        """Connexion → accès au dashboard"""
        response = authenticated_client.get('/')
        assert response.status_code == 200
        assert b'skillboard' in response.data.lower() or b'dashboard' in response.data.lower()

    def test_workflow_create_competence(self, app, authenticated_client):
        """Créer une compétence via formulaire"""
        response = authenticated_client.post('/add_competence', data={
            'nom_competence': 'Python'
        }, follow_redirects=True)

        assert response.status_code == 200
        with app.app_context():
            comp = db.session.scalars(select(Competence).where(Competence.nom == 'Python')).first()
            assert comp is not None

    def test_workflow_create_poste_with_competences(self, app, authenticated_client):
        """Créer un poste avec compétences liées"""
        with app.app_context():
            c1 = Competence(nom='Python')
            c2 = Competence(nom='Flask')
            db.session.add_all([c1, c2])
            db.session.commit()
            c1_id, c2_id = c1.id, c2.id

        response = authenticated_client.post('/add_poste', data={
            'nom_poste': 'Développeur Python',
            'competences': [str(c1_id), str(c2_id)]
        }, follow_redirects=True)

        assert response.status_code == 200
        with app.app_context():
            poste = db.session.scalars(select(Poste).where(Poste.nom == 'Développeur Python')).first()
            assert poste is not None
            assert len(poste.competences) == 2

    def test_workflow_create_interview(self, app, authenticated_client):
        """Créer un entretien complet"""
        with app.app_context():
            poste = Poste(nom='Dev Python')
            db.session.add(poste)
            db.session.commit()

        response = authenticated_client.post('/create_interview', data={
            'cand_nom': 'Dupont',
            'cand_prenom': 'Jean',
            'entr_poste': 'Dev Python',
            'entr_date': '2026-03-15',
            'entr_recruteur': 'Marie'
        }, follow_redirects=True)

        assert response.status_code == 200
        with app.app_context():
            entretien = db.session.scalars(select(Entretien).where(Entretien.candidat_nom == 'Dupont')).first()
            assert entretien is not None
            assert entretien.candidat_prenom == 'Jean'
            assert entretien.statut == 'Cree'
            assert isinstance(entretien.date_entretien, date)

    def test_workflow_entretien_with_evaluations(self, app, authenticated_client):
        """Entretien → ajout d'évaluations"""
        with app.app_context():
            comp = Competence(nom='Python')
            poste = Poste(nom='Dev', competences=[comp])
            entretien = Entretien(
                candidat_nom='Test',
                candidat_prenom='Candidat',
                date_entretien=date(2026, 3, 15),
                poste_id=poste.id
            )
            db.session.add_all([comp, poste, entretien])
            db.session.commit()
            entretien_id = entretien.id
            competence_id = comp.id

        with app.app_context():
            ev = Evaluation(
                entretien_id=entretien_id,
                competence_id=competence_id,
                note_rh=8, note_recruteur2=7
            )
            db.session.add(ev)
            db.session.commit()

        with app.app_context():
            entretien = db.session.get(Entretien, entretien_id)
            assert len(entretien.evaluations) == 1
            assert entretien.evaluations[0].note_rh == 8

    def test_workflow_fetch_poste_details(self, app, authenticated_client):
        """Récupérer les détails d'un poste via l'API JSON"""
        with app.app_context():
            c1 = Competence(nom='Python')
            c2 = Competence(nom='Flask')
            poste = Poste(nom='Dev Python', competences=[c1, c2])
            db.session.add_all([c1, c2, poste])
            db.session.commit()
            poste_id = poste.id

        response = authenticated_client.get(f'/api/poste/{poste_id}')
        assert response.status_code == 200
        data = response.get_json()
        assert data['nom'] == 'Dev Python'
        assert len(data['competences']) == 2


class TestMultiStepOperations:
    """Opérations multi-étapes"""

    def test_update_poste_competences(self, app, authenticated_client):
        """Mise à jour des compétences d'un poste"""
        with app.app_context():
            c1 = Competence(nom='Python')
            c2 = Competence(nom='Java')
            c3 = Competence(nom='Flask')
            poste = Poste(nom='Dev', competences=[c1])
            db.session.add_all([c1, c2, c3, poste])
            db.session.commit()
            poste_id, c2_id, c3_id = poste.id, c2.id, c3.id

        response = authenticated_client.post('/update_poste', data={
            'poste_id': str(poste_id),
            'nom_poste': 'Dev Backend',
            'competences': [str(c2_id), str(c3_id)]
        }, follow_redirects=True)

        assert response.status_code == 200
        with app.app_context():
            poste = db.session.get(Poste, poste_id)
            assert poste.nom == 'Dev Backend'
            assert len(poste.competences) == 2

    def test_delete_poste_via_api(self, app, authenticated_client):
        """Suppression d'un poste via API JSON"""
        with app.app_context():
            poste = Poste(nom='To Delete')
            db.session.add(poste)
            db.session.commit()
            poste_id = poste.id

        response = authenticated_client.delete(f'/api/poste/{poste_id}')
        assert response.status_code == 200
        assert response.get_json()['success'] == True

        with app.app_context():
            assert db.session.get(Poste, poste_id) is None

    def test_delete_nonexistent_poste(self, authenticated_client):
        """Suppression d'un poste inexistant retourne 404"""
        response = authenticated_client.delete('/api/poste/99999')
        assert response.status_code == 404


class TestAuthenticationFlow:
    """Flux d'authentification"""

    def test_cannot_access_protected_routes_without_auth(self, client):
        """Routes protégées inaccessibles sans authentification"""
        for route in ['/', '/logout']:
            response = client.get(route)
            assert response.status_code == 302

    def test_session_persistence_across_requests(self, authenticated_client):
        """La session persiste entre les requêtes"""
        assert authenticated_client.get('/').status_code == 200
        assert authenticated_client.get('/').status_code == 200

    def test_logout_clears_session(self, authenticated_client):
        """La déconnexion efface la session"""
        assert authenticated_client.get('/').status_code == 200
        authenticated_client.get('/logout')
        assert authenticated_client.get('/').status_code == 302


class TestMonoAdmin:
    """Vérification du design mono-administrateur"""

    def test_register_blocked_when_user_already_exists(self, app, client):
        """La page d'inscription est bloquée si un utilisateur existe déjà (design mono-admin)"""
        with app.app_context():
            user = User(username='admin')
            user.set_password('admin123')
            db.session.add(user)
            db.session.commit()

        # Un visiteur non connecté ne peut pas accéder à /register
        response = client.get('/register', follow_redirects=False)
        assert response.status_code == 302
        assert '/login' in response.headers['Location']

    def test_register_post_blocked_when_user_already_exists(self, app, client):
        """Un POST sur /register est bloqué si un utilisateur existe déjà"""
        with app.app_context():
            user = User(username='admin')
            user.set_password('admin123')
            db.session.add(user)
            db.session.commit()

        response = client.post('/register', data={
            'username': 'intrus',
            'password': 'tentative123'
        }, follow_redirects=False)

        assert response.status_code == 302
        with app.app_context():
            intrus = db.session.scalars(select(User).where(User.username == 'intrus')).first()
            assert intrus is None