"""
Tests unitaires pour les modèles de données
"""
import pytest
from app import create_app
from app.extensions import db
from app.models import User, Competence, Poste, Entretien, Evaluation
from werkzeug.security import check_password_hash


@pytest.fixture
def app():
    """Crée une application de test"""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Crée un client de test"""
    return app.test_client()


class TestUserModel:
    """Tests pour le modèle User"""
    
    def test_user_creation(self, app):
        """✅ Test la création d'un utilisateur"""
        with app.app_context():
            user = User(username='testuser')
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()
            
            assert user.id is not None
            assert user.username == 'testuser'
            assert user.password_hash is not None
    
    def test_user_password_hashing(self, app):
        """✅ Test le hachage du mot de passe"""
        with app.app_context():
            user = User(username='testuser')
            user.set_password('mypassword')
            
            # Le hash ne doit pas être égal au mot de passe
            assert user.password_hash != 'mypassword'
            # Mais la vérification doit fonctionner
            assert user.check_password('mypassword')
            # Un mauvais mot de passe doit échouer
            assert not user.check_password('wrongpassword')
    
    def test_username_unique(self, app):
        """✅ Test que les usernames sont uniques"""
        with app.app_context():
            user1 = User(username='duplicate')
            user1.set_password('pass1')
            db.session.add(user1)
            db.session.commit()
            
            user2 = User(username='duplicate')
            user2.set_password('pass2')
            db.session.add(user2)
            
            with pytest.raises(Exception):  # IntegrityError
                db.session.commit()


class TestCompetenceModel:
    """Tests pour le modèle Competence"""
    
    def test_competence_creation(self, app):
        """✅ Test la création d'une compétence"""
        with app.app_context():
            comp = Competence(nom='Python')
            db.session.add(comp)
            db.session.commit()
            
            assert comp.id is not None
            assert comp.nom == 'Python'
    
    def test_competence_invalid_empty(self, app):
        """✅ Test qu'une compétence ne peut pas être vide"""
        with app.app_context():
            comp = Competence(nom=None)
            db.session.add(comp)
            
            with pytest.raises(Exception):
                db.session.commit()


class TestPosteModel:
    """Tests pour le modèle Poste"""
    
    def test_poste_creation(self, app):
        """✅ Test la création d'un poste"""
        with app.app_context():
            poste = Poste(nom='Développeur')
            db.session.add(poste)
            db.session.commit()
            
            assert poste.id is not None
            assert poste.nom == 'Développeur'
    
    def test_poste_with_competences(self, app):
        """✅ Test un poste avec compétences"""
        with app.app_context():
            c1 = Competence(nom='Python')
            c2 = Competence(nom='Flask')
            poste = Poste(nom='Dev Python', competences=[c1, c2])
            
            db.session.add(poste)
            db.session.commit()
            
            assert len(poste.competences) == 2
            assert c1 in poste.competences
            assert c2 in poste.competences


class TestEntretienModel:
    """Tests pour le modèle Entretien"""
    
    def test_entretien_creation(self, app):
        """✅ Test la création d'un entretien"""
        with app.app_context():
            poste = Poste(nom='Dev')
            db.session.add(poste)
            db.session.commit()
            
            entretien = Entretien(
                candidat_nom='Dupont',
                candidat_prenom='Jean',
                date_entretien='2026-02-28',
                recruteur_secondaire='Marie',
                poste_id=poste.id,
                statut='Cree'
            )
            db.session.add(entretien)
            db.session.commit()
            
            assert entretien.id is not None
            assert entretien.candidat_nom == 'Dupont'
    
    def test_entretien_token_unique(self, app):
        """✅ Test que les tokens d'entretien sont uniques"""
        with app.app_context():
            poste = Poste(nom='Dev')
            db.session.add(poste)
            db.session.commit()
            
            token = 'unique-token-123'
            entretien1 = Entretien(
                candidat_nom='Test1',
                candidat_prenom='A',
                date_entretien='2026-02-28',
                poste_id=poste.id,
                token_recruteur2=token
            )
            db.session.add(entretien1)
            db.session.commit()
            
            entretien2 = Entretien(
                candidat_nom='Test2',
                candidat_prenom='B',
                date_entretien='2026-02-28',
                poste_id=poste.id,
                token_recruteur2=token
            )
            db.session.add(entretien2)
            
            with pytest.raises(Exception):
                db.session.commit()


class TestEvaluationModel:
    """Tests pour le modèle Evaluation"""
    
    def test_evaluation_creation(self, app):
        """✅ Test la création d'une évaluation"""
        with app.app_context():
            poste = Poste(nom='Dev')
            competence = Competence(nom='Python')
            db.session.add_all([poste, competence])
            db.session.commit()
            
            entretien = Entretien(
                candidat_nom='Test',
                candidat_prenom='A',
                date_entretien='2026-02-28',
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