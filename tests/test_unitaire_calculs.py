"""
Tests unitaires pour les calculs de statistiques
"""
import pytest
from app import create_app
from app.extensions import db
from app.models import Competence, Poste, Entretien, Evaluation
import app.calculs as calculs


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


class TestCalculStat:
    """Tests pour la fonction calculer_stat"""
    
    def test_calculer_stat_empty_list(self, app):
        """✅ Test calculer_stat avec liste vide"""
        with app.app_context():
            result = calculs.calculer_stat([])
            assert result is not None
            assert "details" in result
    
    def test_calculer_stat_with_evaluations(self, app):
        """✅ Test calculer_stat avec évaluations"""
        with app.app_context():
            poste = Poste(nom='Dev')
            comp1 = Competence(nom='Python')
            comp2 = Competence(nom='Flask')
            db.session.add_all([poste, comp1, comp2])
            db.session.commit()
            
            entretien = Entretien(
                candidat_nom='Test',
                candidat_prenom='A',
                date_entretien='2026-02-28',
                poste_id=poste.id
            )
            db.session.add(entretien)
            db.session.commit()
            
            eval1 = Evaluation(
                entretien_id=entretien.id,
                competence_id=comp1.id,
                note_rh=8,
                note_recruteur2=9
            )
            eval2 = Evaluation(
                entretien_id=entretien.id,
                competence_id=comp2.id,
                note_rh=7,
                note_recruteur2=8
            )
            db.session.add_all([eval1, eval2])
            db.session.commit()
            
            evaluations = entretien.evaluations
            result = calculs.calculer_stat(evaluations)
            
            assert result is not None
            assert "details" in result