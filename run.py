from app import create_app
import logging
import traceback

# Config logging
logging.basicConfig(
    level=logging.DEBUG,  # ← Passer en DEBUG pour voir tous les messages
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

try:
    app = create_app()
    
    print("\n" + "="*60)
    print("✅ Application SkillBoard démarrée !")
    print("="*60)
    print("   🌐 Web:  http://localhost:5000")
    print("   📊 API:  http://localhost:5000/api/v1/docs")
    print("   📋 ReDoc: http://localhost:5000/api/v1/redoc")
    print("="*60 + "\n")
    
    # Afficher les routes disponibles
    print("📍 Routes disponibles:")
    for rule in app.url_map.iter_rules():
        print(f"   {rule.rule} → {rule.endpoint}")
    print()
    
    app.run(debug=True, host='localhost', port=5000)

except Exception as e:
    print(f"\n❌ ERREUR AU DÉMARRAGE:")
    print(f"{type(e).__name__}: {e}")
    print("\n" + traceback.format_exc())