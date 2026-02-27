"""
Script de test pour vérifier les imports
"""
print("1. Import Flask...")
from flask import Flask
print("   ✅ OK")

print("2. Import config...")
from config import Config
print("   ✅ OK")

print("3. Import extensions...")
from app.extensions import db, login_manager, cache
print("   ✅ OK")

print("4. Import models...")
from app.models import User, Competence, Poste, Entretien, Evaluation
print("   ✅ OK")

print("5. Import routes...")
from app.routes import bp
print("   ✅ OK")

print("6. Import API...")
try:
    from app.api import api_bp
    print("   ✅ OK")
except Exception as e:
    print(f"   ❌ ERREUR: {e}")
    import traceback
    traceback.print_exc()

print("\n✅ Tous les imports fonctionnent!")