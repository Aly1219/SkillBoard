"""
Tests d'intégration — API JSON interne.
Couvre les endpoints /api/poste et /api/competence du blueprint principal.
"""
import pytest
from sqlalchemy import select
from app.extensions import db
from app.models import Competence, Poste, Entretien, Evaluation
from datetime import date


# ============================================================
# POSTES — GET / DELETE
# ============================================================

class TestAPIPoste:

    def test_get_poste_retourne_json(self, app, authenticated_client):
        """GET /api/poste/<id> retourne le nom et les compétences en JSON"""
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
        noms = [c['nom'] for c in data['competences']]
        assert 'Python' in noms
        assert 'Flask' in noms

    def test_get_poste_inexistant_retourne_404(self, authenticated_client):
        """GET /api/poste/<id> sur un ID inexistant retourne 404"""
        response = authenticated_client.get('/api/poste/99999')
        assert response.status_code == 404

    def test_get_poste_sans_authentification_redirige(self, client):
        """GET /api/poste/<id> sans connexion redirige vers login"""
        response = client.get('/api/poste/1')
        assert response.status_code == 302

    def test_delete_poste_retourne_succes(self, app, authenticated_client):
        """DELETE /api/poste/<id> supprime le poste et retourne success=True"""
        with app.app_context():
            poste = Poste(nom='A Supprimer')
            db.session.add(poste)
            db.session.commit()
            poste_id = poste.id

        response = authenticated_client.delete(f'/api/poste/{poste_id}')
        assert response.status_code == 200
        assert response.get_json()['success'] is True

        with app.app_context():
            assert db.session.get(Poste, poste_id) is None

    def test_delete_poste_inexistant_retourne_404(self, authenticated_client):
        """DELETE /api/poste/<id> sur un ID inexistant retourne 404"""
        response = authenticated_client.delete('/api/poste/99999')
        assert response.status_code == 404
        assert response.get_json()['success'] is False


# ============================================================
# COMPÉTENCES — PUT / DELETE
# ============================================================

class TestAPICompetence:

    def test_update_competence_renomme(self, app, authenticated_client):
        """PUT /api/competence/<id> renomme la compétence"""
        with app.app_context():
            comp = Competence(nom='Ancien Nom')
            db.session.add(comp)
            db.session.commit()
            comp_id = comp.id

        response = authenticated_client.put(
            f'/api/competence/{comp_id}',
            json={'nom': 'Nouveau Nom'}
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data['success'] is True
        assert data['competence']['nom'] == 'Nouveau Nom'

    def test_update_competence_nom_vide_retourne_400(self, app, authenticated_client):
        """PUT /api/competence/<id> avec nom vide retourne 400"""
        with app.app_context():
            comp = Competence(nom='Test')
            db.session.add(comp)
            db.session.commit()
            comp_id = comp.id

        response = authenticated_client.put(
            f'/api/competence/{comp_id}',
            json={'nom': '   '}
        )
        assert response.status_code == 400

    def test_update_competence_nom_doublon_retourne_409(self, app, authenticated_client):
        """PUT /api/competence/<id> avec un nom déjà pris retourne 409"""
        with app.app_context():
            c1 = Competence(nom='Python')
            c2 = Competence(nom='Flask')
            db.session.add_all([c1, c2])
            db.session.commit()
            c2_id = c2.id

        response = authenticated_client.put(
            f'/api/competence/{c2_id}',
            json={'nom': 'Python'}
        )
        assert response.status_code == 409

    def test_update_competence_inexistante_retourne_404(self, authenticated_client):
        """PUT /api/competence/<id> sur un ID inexistant retourne 404"""
        response = authenticated_client.put(
            '/api/competence/99999',
            json={'nom': 'Nouveau'}
        )
        assert response.status_code == 404

    def test_delete_competence_libre(self, app, authenticated_client):
        """DELETE /api/competence/<id> supprime une compétence non liée"""
        with app.app_context():
            comp = Competence(nom='A Supprimer')
            db.session.add(comp)
            db.session.commit()
            comp_id = comp.id

        response = authenticated_client.delete(f'/api/competence/{comp_id}')
        assert response.status_code == 200
        assert response.get_json()['success'] is True

        with app.app_context():
            assert db.session.get(Competence, comp_id) is None

    def test_delete_competence_liee_a_poste_retourne_409(self, app, authenticated_client):
        """DELETE /api/competence/<id> bloqué si la compétence est liée à un poste"""
        with app.app_context():
            comp = Competence(nom='Python')
            poste = Poste(nom='Dev', competences=[comp])
            db.session.add_all([comp, poste])
            db.session.commit()
            comp_id = comp.id

        response = authenticated_client.delete(f'/api/competence/{comp_id}')
        assert response.status_code == 409
        assert response.get_json()['success'] is False

    def test_delete_competence_inexistante_retourne_404(self, authenticated_client):
        """DELETE /api/competence/<id> sur un ID inexistant retourne 404"""
        response = authenticated_client.delete('/api/competence/99999')
        assert response.status_code == 404
