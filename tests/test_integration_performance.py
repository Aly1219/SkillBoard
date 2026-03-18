"""
Tests d'intégration — Performance et intégrité des données.
"""
import pytest
import time
from datetime import date
from app.extensions import db
from app.models import User, Competence, Poste, Entretien, Evaluation


# Fixtures app et client supprimées — définies dans conftest.py


class TestPerformance:
    """Tests de performance — temps de réponse sous charge"""

    def test_dashboard_charge_rapidement(self, app, authenticated_client):
        """Le dashboard doit se charger en moins de 2 secondes avec 50 entretiens"""
        with app.app_context():
            entretiens = [
                Entretien(
                    candidat_nom=f'Candidat{i}',
                    candidat_prenom=f'Test{i}',
                    date_entretien=date(2026, 3, 15),
                    poste_id=None
                )
                for i in range(50)
            ]
            db.session.add_all(entretiens)
            db.session.commit()

        start = time.time()
        response = authenticated_client.get('/')
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 2.0, f"Dashboard trop lent : {elapsed:.2f}s"

    def test_creation_en_masse_competences(self, app, authenticated_client):
        """Créer 10 compétences doit prendre moins de 5 secondes"""
        start = time.time()
        for i in range(10):
            authenticated_client.post('/add_competence', data={
                'nom_competence': f'Skill{i}'
            })
        elapsed = time.time() - start

        assert elapsed < 5.0, f"Création en masse trop lente : {elapsed:.2f}s"
        with app.app_context():
            assert Competence.query.count() >= 10

    def test_requete_competences_rapide(self, app):
        """Une requête sur 50 compétences doit s'exécuter en moins de 500ms"""
        with app.app_context():
            db.session.add_all([Competence(nom=f'Comp{i}') for i in range(50)])
            db.session.commit()

            start = time.time()
            comps = Competence.query.all()
            elapsed = time.time() - start

            assert len(comps) >= 50
            assert elapsed < 0.5, f"Requête trop lente : {elapsed:.3f}s"


class TestDataIntegrity:
    """Tests de l'intégrité des données"""

    def test_contrainte_unique_username(self, app):
        """Deux utilisateurs avec le même username doivent lever une exception"""
        with app.app_context():
            u1 = User(username='duplicate')
            u1.set_password('pass1')
            db.session.add(u1)
            db.session.commit()

            u2 = User(username='duplicate')
            u2.set_password('pass2')
            db.session.add(u2)
            with pytest.raises(Exception):
                db.session.commit()

    def test_contrainte_unique_poste(self, app):
        """Deux postes avec le même nom doivent lever une exception"""
        with app.app_context():
            db.session.add(Poste(nom='Dev'))
            db.session.commit()
            db.session.add(Poste(nom='Dev'))
            with pytest.raises(Exception):
                db.session.commit()

    def test_relation_entretien_evaluations(self, app):
        """Les évaluations sont bien liées à leur entretien"""
        with app.app_context():
            c1 = Competence(nom='Python')
            c2 = Competence(nom='Flask')
            entretien = Entretien(
                candidat_nom='Test',
                candidat_prenom='Candidat',
                date_entretien=date(2026, 3, 15),
                poste_id=None
            )
            db.session.add_all([c1, c2, entretien])
            db.session.flush()

            db.session.add_all([
                Evaluation(
                    entretien_id=entretien.id,
                    competence_id=c1.id,
                    note_rh=8, note_recruteur2=7
                ),
                Evaluation(
                    entretien_id=entretien.id,
                    competence_id=c2.id,
                    note_rh=9, note_recruteur2=8
                )
            ])
            db.session.commit()

            reloaded = db.session.get(Entretien, entretien.id)
            assert len(reloaded.evaluations) == 2
            notes_rh = {ev.note_rh for ev in reloaded.evaluations}
            assert notes_rh == {8, 9}

    def test_suppression_entretien_sans_cascade(self, app):
        """Les évaluations d'un entretien sont bien retrouvées avant suppression"""
        with app.app_context():
            comp = Competence(nom='Python')
            entretien = Entretien(
                candidat_nom='Test', candidat_prenom='A',
                date_entretien=date(2026, 3, 15), poste_id=None
            )
            db.session.add_all([comp, entretien])
            db.session.flush()

            ev = Evaluation(
                entretien_id=entretien.id,
                competence_id=comp.id,
                note_rh=7, note_recruteur2=8
            )
            db.session.add(ev)
            db.session.commit()

            entretien_id = entretien.id
            reloaded = db.session.get(Entretien, entretien_id)
            assert len(reloaded.evaluations) == 1