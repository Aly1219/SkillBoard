"""
Tests d'intégration - Performance et charge
Teste le comportement sous différentes charges
"""
import pytest
import time
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


class TestPerformance:
    """Tests de performance"""
    
    def test_load_dashboard_with_many_entretiens(self, app, client):
        """✅ Test chargement du dashboard avec plusieurs entretiens"""
        
        with app.app_context():
            # Créer un utilisateur
            user = User(username='admin')
            user.set_password('admin')
            db.session.add(user)
            
            # Créer plusieurs postes et entretiens
            postes = [Poste(nom=f'Poste {i}') for i in range(10)]
            entretiens = [
                Entretien(
                    candidat_nom=f'Candidat{i}',
                    candidat_prenom=f'Test{i}',
                    date_entretien='2026-03-15',
                    poste_id=None
                )
                for i in range(50)
            ]
            
            db.session.add_all(postes + entretiens + [user])
            db.session.commit()
        
        # Connecter
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin'
        })
        
        # Mesurer le temps de chargement du dashboard
        start = time.time()
        response = client.get('/')
        end = time.time()
        
        assert response.status_code == 200
        assert (end - start) < 2.0  # Doit charger en moins de 2 secondes
    
    def test_bulk_competence_creation(self, app, client):
        """✅ Test création en masse de compétences"""
        
        with app.app_context():
            user = User(username='admin')
            user.set_password('admin')
            db.session.add(user)
            db.session.commit()
        
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin'
        })
        
        start = time.time()
        
        # Créer 10 compétences
        for i in range(10):
            client.post('/add_competence', data={
                'nom_competence': f'Skill{i}'
            })
        
        end = time.time()
        
        with app.app_context():
            # ✅ Compter sans les 3 compétences par défaut
            count = Competence.query.count()
            # Doit avoir créé au moins 10 compétences (+ 3 par défaut = 13+)
            assert count >= 13
            # Doit être rapide (moins de 5 secondes)
            assert (end - start) < 5.0
    
    def test_query_efficiency(self, app):
        """✅ Test que les requêtes sont efficaces"""
        
        with app.app_context():
            # Créer 50 compétences (+ 3 par défaut)
            competences = [Competence(nom=f'Comp{i}') for i in range(50)]
            db.session.add_all(competences)
            db.session.commit()
            
            # Mesurer le temps de requête
            start = time.time()
            comps = Competence.query.all()
            end = time.time()
            
            # ✅ Doit avoir 50 + 3 (par défaut)
            assert len(comps) >= 50
            assert (end - start) < 0.5  # Doit être très rapide


class TestDataIntegrity:
    """Tests de l'intégrité des données"""
    
    def test_unique_constraints(self, app):
        """✅ Test que les contraintes UNIQUE fonctionnent"""
        
        with app.app_context():
            # Créer deux utilisateurs avec le même username
            user1 = User(username='duplicate')
            user1.set_password('pass1')
            db.session.add(user1)
            db.session.commit()
            
            user2 = User(username='duplicate')
            user2.set_password('pass2')
            db.session.add(user2)
            
            # Doit lever une exception
            with pytest.raises(Exception):
                db.session.commit()
    
    def test_entretien_with_evaluations_relationship(self, app):
        """✅ Test la relation entre entretien et évaluations"""
        
        with app.app_context():
            # Créer des données
            poste = Poste(nom='Dev')
            comp1 = Competence(nom='Python')
            comp2 = Competence(nom='Flask')
            entretien = Entretien(
                candidat_nom='Test',
                candidat_prenom='Candidat',
                date_entretien='2026-03-15',
                poste_id=None
            )
            
            db.session.add_all([poste, comp1, comp2, entretien])
            db.session.flush()
            
            # Ajouter des évaluations
            eval1 = Evaluation(
                entretien_id=entretien.id,
                competence_id=comp1.id,
                note_rh=8,
                note_recruteur2=7
            )
            eval2 = Evaluation(
                entretien_id=entretien.id,
                competence_id=comp2.id,
                note_rh=9,
                note_recruteur2=8
            )
            db.session.add_all([eval1, eval2])
            db.session.commit()
            
            # Vérifier la relation
            entretien_check = db.session.get(Entretien, entretien.id)
            assert len(entretien_check.evaluations) == 2
            assert entretien_check.evaluations[0].note_rh == 8
            assert entretien_check.evaluations[1].note_rh == 9