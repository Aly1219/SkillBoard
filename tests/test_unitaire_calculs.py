"""
Tests unitaires pour les calculs de statistiques.
Couvre la logique métier centrale de l'application.
"""
import pytest
from datetime import date
from app.extensions import db
from app.models import Competence, Poste, Entretien, Evaluation
import app.calculs as calculs


# ============================================================
# HELPERS
# ============================================================

def make_evaluation(app, entretien_id, competence_id, note_rh, note_rec2, palier=7):
    """Crée une évaluation de test avec les notes et palier donnés"""
    with app.app_context():
        ev = Evaluation(
            entretien_id=entretien_id,
            competence_id=competence_id,
            note_rh=note_rh,
            note_recruteur2=note_rec2,
            palier=palier
        )
        db.session.add(ev)
        db.session.commit()


def setup_entretien(app):
    """Crée un entretien de base avec deux compétences, retourne les IDs"""
    with app.app_context():
        c1 = Competence(nom='Python')
        c2 = Competence(nom='Flask')
        poste = Poste(nom='Dev', competences=[c1, c2])
        entretien = Entretien(
            candidat_nom='Test',
            candidat_prenom='A',
            date_entretien=date(2026, 3, 15),
            poste_id=None
        )
        db.session.add_all([c1, c2, poste, entretien])
        db.session.flush()
        ids = {
            'entretien_id': entretien.id,
            'c1_id': c1.id,
            'c2_id': c2.id
        }
        db.session.commit()
        return ids


# ============================================================
# TESTS
# ============================================================

class TestCalculerStatListeVide:
    """Cas limite — liste vide"""

    def test_retourne_un_dict(self, app):
        """calculer_stat([]) doit retourner un dict et non lever d'exception"""
        with app.app_context():
            result = calculs.calculer_stat([])
            assert isinstance(result, dict)

    def test_toutes_les_cles_presentes(self, app):
        """Toutes les clés attendues sont présentes même avec une liste vide"""
        with app.app_context():
            result = calculs.calculer_stat([])
            cles_attendues = [
                'details', 'details_tries', 'moy_generale', 'palier_moyen',
                'meilleure_competence', 'meilleure_note',
                'pire_competence', 'pire_note',
                'competences_sous_palier', 'nombre_sous_palier', 'pourcentage_sous_palier'
            ]
            for cle in cles_attendues:
                assert cle in result, f"Clé manquante : {cle}"

    def test_valeurs_neutres(self, app):
        """Avec une liste vide, les valeurs numériques doivent être à 0"""
        with app.app_context():
            result = calculs.calculer_stat([])
            assert result['moy_generale'] == 0
            assert result['nombre_sous_palier'] == 0
            assert result['pourcentage_sous_palier'] == 0


class TestCalculerStatValeurs:
    """Vérification des valeurs calculées"""

    def test_moyenne_generale_correcte(self, app):
        """Moyenne générale = (8.5 + 7.5) / 2 = 8.0"""
        ids = setup_entretien(app)
        make_evaluation(app, ids['entretien_id'], ids['c1_id'], note_rh=8, note_rec2=9, palier=7)
        make_evaluation(app, ids['entretien_id'], ids['c2_id'], note_rh=7, note_rec2=8, palier=7)

        with app.app_context():
            entretien = db.session.get(Entretien, ids['entretien_id'])
            result = calculs.calculer_stat(entretien.evaluations)
            assert result['moy_generale'] == 8.0

    def test_meilleure_competence(self, app):
        """La meilleure compétence est celle avec la note la plus haute"""
        ids = setup_entretien(app)
        make_evaluation(app, ids['entretien_id'], ids['c1_id'], note_rh=9, note_rec2=9, palier=7)
        make_evaluation(app, ids['entretien_id'], ids['c2_id'], note_rh=5, note_rec2=5, palier=7)

        with app.app_context():
            entretien = db.session.get(Entretien, ids['entretien_id'])
            result = calculs.calculer_stat(entretien.evaluations)
            assert result['meilleure_note'] == 9.0
            assert result['meilleure_competence'] == 'Python'

    def test_pire_competence(self, app):
        """La pire compétence est celle avec la note la plus basse"""
        ids = setup_entretien(app)
        make_evaluation(app, ids['entretien_id'], ids['c1_id'], note_rh=9, note_rec2=9, palier=7)
        make_evaluation(app, ids['entretien_id'], ids['c2_id'], note_rh=4, note_rec2=4, palier=7)

        with app.app_context():
            entretien = db.session.get(Entretien, ids['entretien_id'])
            result = calculs.calculer_stat(entretien.evaluations)
            assert result['pire_note'] == 4.0
            assert result['pire_competence'] == 'Flask'

    def test_details_tries_ordre_decroissant(self, app):
        """details_tries doit être trié par moyenne décroissante"""
        ids = setup_entretien(app)
        make_evaluation(app, ids['entretien_id'], ids['c1_id'], note_rh=4, note_rec2=4, palier=7)
        make_evaluation(app, ids['entretien_id'], ids['c2_id'], note_rh=9, note_rec2=9, palier=7)

        with app.app_context():
            entretien = db.session.get(Entretien, ids['entretien_id'])
            result = calculs.calculer_stat(entretien.evaluations)
            moyennes = [d['moyenne'] for d in result['details_tries']]
            assert moyennes == sorted(moyennes, reverse=True)


class TestCalculerStatPalier:
    """Vérification de la logique de palier"""

    def test_toutes_competences_au_dessus_palier(self, app):
        """Aucune compétence sous palier si toutes les moyennes >= palier"""
        ids = setup_entretien(app)
        make_evaluation(app, ids['entretien_id'], ids['c1_id'], note_rh=8, note_rec2=8, palier=7)
        make_evaluation(app, ids['entretien_id'], ids['c2_id'], note_rh=9, note_rec2=9, palier=7)

        with app.app_context():
            entretien = db.session.get(Entretien, ids['entretien_id'])
            result = calculs.calculer_stat(entretien.evaluations)
            assert result['nombre_sous_palier'] == 0
            assert result['pourcentage_sous_palier'] == 0.0

    def test_une_competence_sous_palier(self, app):
        """Une compétence sous palier sur deux = 50%"""
        ids = setup_entretien(app)
        make_evaluation(app, ids['entretien_id'], ids['c1_id'], note_rh=8, note_rec2=8, palier=7)
        make_evaluation(app, ids['entretien_id'], ids['c2_id'], note_rh=4, note_rec2=4, palier=7)

        with app.app_context():
            entretien = db.session.get(Entretien, ids['entretien_id'])
            result = calculs.calculer_stat(entretien.evaluations)
            assert result['nombre_sous_palier'] == 1
            assert result['pourcentage_sous_palier'] == 50.0

    def test_toutes_competences_sous_palier(self, app):
        """Toutes les compétences sous palier = 100%"""
        ids = setup_entretien(app)
        make_evaluation(app, ids['entretien_id'], ids['c1_id'], note_rh=3, note_rec2=3, palier=7)
        make_evaluation(app, ids['entretien_id'], ids['c2_id'], note_rh=4, note_rec2=4, palier=7)

        with app.app_context():
            entretien = db.session.get(Entretien, ids['entretien_id'])
            result = calculs.calculer_stat(entretien.evaluations)
            assert result['nombre_sous_palier'] == 2
            assert result['pourcentage_sous_palier'] == 100.0

    def test_palier_defaut_utilise(self, app):
        """Si palier non défini, PALIER_DEFAUT est utilisé"""
        ids = setup_entretien(app)
        with app.app_context():
            ev = Evaluation(
                entretien_id=ids['entretien_id'],
                competence_id=ids['c1_id'],
                note_rh=5,
                note_recruteur2=5,
                palier=None  # Pas de palier défini
            )
            db.session.add(ev)
            db.session.commit()

            entretien = db.session.get(Entretien, ids['entretien_id'])
            result = calculs.calculer_stat(entretien.evaluations)
            # Moyenne = 5, PALIER_DEFAUT = 7 → sous palier
            assert result['nombre_sous_palier'] == 1


class TestCalculerStatEcartVotes:
    """Vérification de la divergence entre recruteurs"""

    def test_ecart_votes_identiques(self, app):
        """Pas d'alerte si les deux recruteurs donnent la même note"""
        ids = setup_entretien(app)
        make_evaluation(app, ids['entretien_id'], ids['c1_id'], note_rh=7, note_rec2=7, palier=5)

        with app.app_context():
            entretien = db.session.get(Entretien, ids['entretien_id'])
            result = calculs.calculer_stat(entretien.evaluations)
            assert result['details'][0]['ecart_votes'] == 0
            assert result['details'][0]['alerte_recr'] == False

    def test_ecart_votes_divergents(self, app):
        """Alerte si les deux recruteurs divergent"""
        ids = setup_entretien(app)
        make_evaluation(app, ids['entretien_id'], ids['c1_id'], note_rh=3, note_rec2=9, palier=5)

        with app.app_context():
            entretien = db.session.get(Entretien, ids['entretien_id'])
            result = calculs.calculer_stat(entretien.evaluations)
            assert result['details'][0]['ecart_votes'] == 6
            assert result['details'][0]['alerte_recr'] == True