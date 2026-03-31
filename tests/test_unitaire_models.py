"""
Tests unitaires pour les modèles de données.
"""
import pytest
from datetime import date
from app.extensions import db
from app.models import User, Competence, Poste, Entretien, Evaluation


# Fixtures app et client supprimées — définies dans conftest.py


class TestUserModel:
    """Tests pour le modèle User"""

    def test_user_creation(self, app):
        with app.app_context():
            user = User(username='testuser')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            assert user.id is not None
            assert user.username == 'testuser'
            assert user.password_hash is not None

    def test_user_password_hashing(self, app):
        with app.app_context():
            user = User(username='testuser')
            user.set_password('mypassword')
            assert user.password_hash != 'mypassword'
            assert user.check_password('mypassword')
            assert not user.check_password('wrongpassword')

    def test_username_unique(self, app):
        with app.app_context():
            user1 = User(username='duplicate')
            user1.set_password('pass1')
            db.session.add(user1)
            db.session.commit()

            user2 = User(username='duplicate')
            user2.set_password('pass2')
            db.session.add(user2)
            with pytest.raises(Exception):
                db.session.commit()

    def test_user_repr(self, app):
        """__repr__ doit contenir le nom d'utilisateur"""
        with app.app_context():
            user = User(username='alice')
            assert 'alice' in repr(user)


class TestCompetenceModel:
    """Tests pour le modèle Competence"""

    def test_competence_creation(self, app):
        with app.app_context():
            comp = Competence(nom='Python')
            db.session.add(comp)
            db.session.commit()
            assert comp.id is not None
            assert comp.nom == 'Python'

    def test_competence_nom_unique(self, app):
        with app.app_context():
            db.session.add(Competence(nom='Python'))
            db.session.commit()
            db.session.add(Competence(nom='Python'))
            with pytest.raises(Exception):
                db.session.commit()

    def test_competence_nom_not_null(self, app):
        with app.app_context():
            comp = Competence(nom=None)
            db.session.add(comp)
            with pytest.raises(Exception):
                db.session.commit()

    def test_competence_repr(self, app):
        with app.app_context():
            comp = Competence(nom='Flask')
            assert 'Flask' in repr(comp)


class TestPosteModel:
    """Tests pour le modèle Poste"""

    def test_poste_creation(self, app):
        with app.app_context():
            poste = Poste(nom='Développeur')
            db.session.add(poste)
            db.session.commit()
            assert poste.id is not None
            assert poste.nom == 'Développeur'

    def test_poste_with_competences(self, app):
        with app.app_context():
            c1 = Competence(nom='Python')
            c2 = Competence(nom='Flask')
            poste = Poste(nom='Dev Python', competences=[c1, c2])
            db.session.add(poste)
            db.session.commit()
            assert len(poste.competences) == 2
            assert c1 in poste.competences
            assert c2 in poste.competences

    def test_poste_nom_unique(self, app):
        with app.app_context():
            db.session.add(Poste(nom='Dev'))
            db.session.commit()
            db.session.add(Poste(nom='Dev'))
            with pytest.raises(Exception):
                db.session.commit()

    def test_poste_repr(self, app):
        with app.app_context():
            poste = Poste(nom='Analyste')
            assert 'Analyste' in repr(poste)


class TestEntretienModel:
    """Tests pour le modèle Entretien"""

    def test_entretien_creation(self, app):
        with app.app_context():
            poste = Poste(nom='Dev')
            db.session.add(poste)
            db.session.commit()

            entretien = Entretien(
                candidat_nom='Dupont',
                candidat_prenom='Jean',
                date_entretien=date(2026, 2, 28),  # objet date — pas une chaîne
                recruteur_secondaire='Marie',
                poste_id=poste.id,
                statut='Cree'
            )
            db.session.add(entretien)
            db.session.commit()
            assert entretien.id is not None
            assert entretien.candidat_nom == 'Dupont'

    def test_entretien_date_est_un_objet_date(self, app):
        """date_entretien doit être stocké et relu comme objet date Python"""
        with app.app_context():
            poste = Poste(nom='Dev')
            db.session.add(poste)
            db.session.commit()

            entretien = Entretien(
                candidat_nom='Test',
                candidat_prenom='A',
                date_entretien=date(2026, 6, 15),
                poste_id=poste.id
            )
            db.session.add(entretien)
            db.session.commit()

            reloaded = db.session.get(Entretien, entretien.id)
            assert isinstance(reloaded.date_entretien, date)
            assert reloaded.date_entretien.year == 2026
            assert reloaded.date_entretien.month == 6
            assert reloaded.date_entretien.day == 15

    def test_entretien_repr(self, app):
        with app.app_context():
            entretien = Entretien(candidat_nom='Martin', candidat_prenom='Léa')
            assert 'Martin' in repr(entretien)


class TestEntretienPinModel:
    """Tests pour le système PIN à usage unique (accès second recruteur)"""

    def test_set_pin_hash_different_de_pin_clair(self, app):
        """Le PIN ne doit jamais être stocké en clair"""
        with app.app_context():
            entretien = Entretien(candidat_nom='Test', candidat_prenom='A')
            entretien.set_pin('123456')
            assert entretien.pin_hash != '123456'
            assert entretien.pin_hash is not None

    def test_check_pin_correct(self, app):
        """check_pin retourne True pour le bon PIN"""
        with app.app_context():
            entretien = Entretien(candidat_nom='Test', candidat_prenom='A')
            entretien.set_pin('654321')
            assert entretien.check_pin('654321') is True

    def test_check_pin_incorrect(self, app):
        """check_pin retourne False pour un PIN erroné"""
        with app.app_context():
            entretien = Entretien(candidat_nom='Test', candidat_prenom='A')
            entretien.set_pin('654321')
            assert entretien.check_pin('000000') is False

    def test_clear_pin_invalide_le_pin(self, app):
        """Après clear_pin, check_pin retourne toujours False — PIN à usage unique"""
        with app.app_context():
            entretien = Entretien(candidat_nom='Test', candidat_prenom='A')
            entretien.set_pin('111222')
            entretien.clear_pin()
            assert entretien.pin_hash is None
            assert entretien.check_pin('111222') is False

    def test_check_pin_sans_pin_defini(self, app):
        """check_pin retourne False si aucun PIN n'a été défini"""
        with app.app_context():
            entretien = Entretien(candidat_nom='Test', candidat_prenom='A')
            assert entretien.check_pin('123456') is False


class TestEvaluationModel:
    """Tests pour le modèle Evaluation"""

    def test_evaluation_creation(self, app):
        with app.app_context():
            poste = Poste(nom='Dev')
            competence = Competence(nom='Python')
            db.session.add_all([poste, competence])
            db.session.commit()

            entretien = Entretien(
                candidat_nom='Test', candidat_prenom='A',
                date_entretien=date(2026, 2, 28),
                poste_id=poste.id
            )
            db.session.add(entretien)
            db.session.commit()

            evaluation = Evaluation(
                entretien_id=entretien.id,
                competence_id=competence.id,
                note_rh=8,
                note_recruteur2=9
            )
            db.session.add(evaluation)
            db.session.commit()

            assert evaluation.id is not None
            assert evaluation.note_rh == 8
            assert evaluation.note_recruteur2 == 9

    def test_evaluation_repr(self, app):
        with app.app_context():
            ev = Evaluation(entretien_id=1, competence_id=2)
            assert '1' in repr(ev)