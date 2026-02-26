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
    print("   🌐 Web:  http://localhost:8000")
    print("   📊 API:  http://localhost:8000/api/v1/docs")
    print("="*60 + "\n")
    
    # Afficher les routes disponibles
    '''
    print("📍 Routes disponibles:")
    for rule in app.url_map.iter_rules():
        print(f"   {rule.rule} → {rule.endpoint}")
    print()
    '''
    
    # ✅ CORRECTION : Utiliser 0.0.0.0 pour Docker
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    app.run(debug=debug, host=host, port=port)

except Exception as e:
    print(f"\n❌ ERREUR AU DÉMARRAGE:")
    print(f"{type(e).__name__}: {e}")
    print("\n" + traceback.format_exc())