import logging
import traceback
import os
from app import create_app

# ============================================================
# LOGGING
# ============================================================
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# ============================================================
# DÉMARRAGE
# ============================================================
try:
    app = create_app()

    host  = os.getenv('FLASK_HOST', '0.0.0.0')
    port  = int(os.getenv('FLASK_PORT', 5001))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

    app.logger.info("Application SkillBoard démarrée")
    app.logger.info(f"Web : http://localhost:{port}")

    if debug:
        # Affiche les routes uniquement en mode debug
        print("\n" + "=" * 60)
        print("  SkillBoard — mode développement")
        print("=" * 60)
        print(f"  Web  : http://localhost:{port}")
        print(f"  API  : http://localhost:{port}/api/v1/docs")
        print("=" * 60)

        print("\nBlueprints enregistrés :")
        for name in app.blueprints:
            print(f"  - {name}")

        print("\nRoutes disponibles :")
        for rule in sorted(app.url_map.iter_rules(), key=lambda r: r.rule):
            if not rule.rule.startswith('/static'):
                print(f"  {rule.rule:45} → {rule.endpoint}")
        print()

    app.run(debug=debug, host=host, port=port)

except Exception as e:
    print(f"\nERREUR AU DÉMARRAGE : {type(e).__name__}: {e}")
    print(traceback.format_exc())