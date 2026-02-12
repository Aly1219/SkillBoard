import os
import sys
from dotenv import load_dotenv
from app.utils import resource_path

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'cle_par_defaut_si_pas_trouvee')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def get_db_uri():
        # Logique PyInstaller pour la DB
        if getattr(sys, "frozen", False):
            # Bundle PyInstaller
            user_data_dir = os.path.join(os.path.expanduser("~"), "Library", "Application Support", "SkillBoard")
            os.makedirs(user_data_dir, exist_ok=True)
            db_path = os.path.join(user_data_dir, "database.db")
            
            # Copie de la DB si inexistante (logique à gérer éventuellement dans init_db, 
            # mais ici on définit juste le chemin)
            bundled_db = resource_path("database.db")
            if not os.path.exists(db_path) and os.path.exists(bundled_db):
                import shutil
                shutil.copyfile(bundled_db, db_path)
        else:
            # Mode dev
            db_path = resource_path("database.db")
        
        return f"sqlite:///{db_path}"
    
    # Config Email
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = int(os.getenv('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS') == 'True'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')

# On assigne l'URI dynamiquement
Config.SQLALCHEMY_DATABASE_URI = Config.get_db_uri()
