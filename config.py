import os
from datetime import timedelta

class Config:
    """Configuration de base pour SkillBoard"""
    
    # ============================================================================
    # BASE DE DONNÉES
    # ============================================================================
    
    # Utiliser un chemin ABSOLU pour Docker
    db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'instance', 'skillboard.db')
    
    # Créer le répertoire s'il n'existe pas
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        f'sqlite:///{db_path}'
    )
    
    # Désactiver les warnings de modification de modèles
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Pool de connexions (utile pour concurrence)
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
    }
    
    # ============================================================================
    # SÉCURITÉ
    # ============================================================================
    
    # Clé secrète (OBLIGATOIRE en production)
    SECRET_KEY = os.getenv(
        'SECRET_KEY',
        'dev-key-change-in-production-asap'
    )
    
    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = os.getenv('FLASK_ENV') == 'production'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # ============================================================================
    # FLASK
    # ============================================================================
    
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    TESTING = False
    
    # ============================================================================
    # CACHE
    # ============================================================================
    
    CACHE_TYPE = os.getenv('CACHE_TYPE', 'SimpleCache')
    CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_DEFAULT_TIMEOUT', '3600'))
    
    # ============================================================================
    # EMAIL (Pour récupération de mot de passe futur)
    # ============================================================================
    
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', '')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@skillboard.com')
    
    # ============================================================================
    # LOGGING
    # ============================================================================
    
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'skillboard.log')
    
    # ============================================================================
    # APPLICATION
    # ============================================================================
    
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file upload
    JSON_SORT_KEYS = False


class DevelopmentConfig(Config):
    """Configuration pour développement"""
    DEBUG = True
    TESTING = False
    SQLALCHEMY_ECHO = True  # Afficher les requêtes SQL


class ProductionConfig(Config):
    """Configuration pour production"""
    DEBUG = False
    TESTING = False
    
    # En production, la SECRET_KEY DOIT être définie
    @staticmethod
    def init_app(app):
        if app.config['SECRET_KEY'] == 'dev-key-change-in-production-asap':
            raise ValueError(
                '⚠️ ERREUR CRITIQUE : SECRET_KEY par défaut en production ! '
                'Définir la variable d\'environnement SECRET_KEY'
            )


class TestingConfig(Config):
    """Configuration pour tests"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


# ============================================================================
# SÉLECTIONNER LA CONFIGURATION
# ============================================================================

config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Retourner la configuration appropriée selon l'environnement"""
    env = os.getenv('FLASK_ENV', 'development')
    return config_by_name.get(env, config_by_name['default'])