"""
Test pour vérifier les imports
"""

def test_import_flask():
    """✅ Teste l'import de Flask"""
    from flask import Flask
    assert Flask is not None
    print("   ✅ Flask OK")

def test_import_config():
    """✅ Teste l'import de config"""
    from config import Config
    assert Config is not None
    print("   ✅ Config OK")

def test_import_extensions():
    """✅ Teste l'import des extensions"""
    from app.extensions import db, login_manager, cache
    assert db is not None
    assert login_manager is not None
    assert cache is not None
    print("   ✅ Extensions OK")

def test_import_models():
    """✅ Teste l'import des modèles"""
    from app.models import User, Competence, Poste, Entretien, Evaluation
    assert User is not None
    assert Competence is not None
    print("   ✅ Models OK")

def test_import_routes():
    """✅ Teste l'import des routes"""
    from app.routes import bp
    assert bp is not None
    print("   ✅ Routes OK")

def test_import_api():
    """✅ Teste l'import de l'API"""
    from app.api import api_bp
    assert api_bp is not None
    print("   ✅ API OK")