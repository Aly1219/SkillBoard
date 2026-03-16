from app import create_app
import logging
import traceback
import os

# Config logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

try:
    app = create_app()
    
    print("\n" + "="*60)
    print("✅ Application SkillBoard démarrée !")
    print("="*60)
    print("   🌐 Web:  http://localhost:5001")
    print("   📊 API:  http://localhost:5001/api/v1/docs")
    print("="*60 + "\n")
    
    # 🔍 DEBUG: Afficher les blueprints enregistrés
    print("\n📍 Blueprints enregistrés:")
    for blueprint_name in app.blueprints:
        print(f"   ✅ {blueprint_name}")
    
    print("\n📍 Routes disponibles:")
    for rule in app.url_map.iter_rules():
        if not rule.rule.startswith('/static'):
            print(f"   {rule.rule} → {rule.endpoint}")
    
    print()
    
    # ✅ CORRECT : Port 5001 pour Docker, host 0.0.0.0
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5001))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    app.run(debug=debug, host=host, port=port)

except Exception as e:
    print(f"\n❌ ERREUR AU DÉMARRAGE:")
    print(f"{type(e).__name__}: {e}")
    print("\n" + traceback.format_exc())