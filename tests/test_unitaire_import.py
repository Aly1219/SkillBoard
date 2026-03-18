"""
Tests de smoke — vérifient que tous les modules s'importent sans erreur.
Utiles pour détecter rapidement les imports cassés.
"""


def test_import_flask():
    from flask import Flask
    assert Flask is not None


def test_import_config():
    from config import Config
    assert Config is not None


def test_import_extensions():
    from app.extensions import db, login_manager, cache
    assert db is not None
    assert login_manager is not None
    assert cache is not None


def test_import_models():
    from app.models import User, Competence, Poste, Entretien, Evaluation
    assert all([User, Competence, Poste, Entretien, Evaluation])


def test_import_routes():
    from app.routes import bp
    assert bp is not None


def test_import_calculs():
    import app.calculs as calculs
    assert hasattr(calculs, 'calculer_stat')
    assert hasattr(calculs, 'PALIER_DEFAUT')


def test_import_utils():
    from app.utils import resource_path, format_date_fr
    assert callable(resource_path)
    assert callable(format_date_fr)


def test_import_validators():
    from app.validators import validate_note_range, validate_string_field
    assert callable(validate_note_range)
    assert callable(validate_string_field)


def test_import_db_helpers():
    from app.db_helpers import get_dashboard_data, get_poste_by_id
    assert callable(get_dashboard_data)
    assert callable(get_poste_by_id)


def test_import_api():
    from app.api import api_bp
    assert api_bp is not None