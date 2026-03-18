"""
Tests unitaires pour les utilitaires.
"""
import pytest
import os
from datetime import date
from app.utils import resource_path, format_date_fr


class TestResourcePath:
    """Tests pour resource_path"""

    def test_resource_path_dev(self):
        """En mode dev, retourne un chemin absolu contenant le dossier demandé"""
        path = resource_path("templates")
        assert "templates" in path
        assert os.path.isabs(path)

    def test_resource_path_returns_absolute(self):
        """Toujours un chemin absolu"""
        path = resource_path("app")
        assert os.path.isabs(path)

    def test_resource_path_with_subdir(self):
        """Fonctionne avec des sous-dossiers"""
        path = resource_path("app/templates/index.html")
        assert "app" in path
        assert "templates" in path
        assert "index.html" in path
        assert os.path.isabs(path)


class TestFormatDateFr:
    """Tests pour format_date_fr"""

    def test_objet_date_natif(self):
        """Convertit un objet date Python en chaîne française"""
        result = format_date_fr(date(2026, 1, 31))
        assert result == "31 janvier 2026"

    def test_chaine_iso(self):
        """Convertit une chaîne ISO 'YYYY-MM-DD' en chaîne française"""
        result = format_date_fr("2026-03-15")
        assert result == "15 mars 2026"

    def test_none_retourne_chaine_vide(self):
        """None retourne une chaîne vide sans lever d'exception"""
        result = format_date_fr(None)
        assert result == ""

    def test_format_invalide_retourne_original(self):
        """Un format inconnu retourne la valeur originale sans planter"""
        result = format_date_fr("pas-une-date")
        assert result == "pas-une-date"

    def test_tous_les_mois(self):
        """Vérifie que les 12 mois sont correctement traduits"""
        mois_attendus = [
            (1, "janvier"), (2, "février"),  (3, "mars"),
            (4, "avril"),   (5, "mai"),      (6, "juin"),
            (7, "juillet"), (8, "août"),     (9, "septembre"),
            (10, "octobre"), (11, "novembre"), (12, "décembre"),
        ]
        for mois_num, mois_nom in mois_attendus:
            result = format_date_fr(date(2026, mois_num, 1))
            assert mois_nom in result, f"Mois {mois_num} mal traduit : {result}"

    def test_premier_du_mois(self):
        """Le jour 1 est affiché sans zéro devant"""
        result = format_date_fr(date(2026, 6, 1))
        assert result == "1 juin 2026"
        assert result.startswith("1 ")  # Pas "01"