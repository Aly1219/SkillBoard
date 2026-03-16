import os
from datetime import timedelta

class Config:
    """Configuration de base pour SkillBoard"""
    
    # ============================================================================
    # BASE DE DONNÉES - SQLite Local (Docker compatible)
    # ============================================================================
    
    # Créer le répertoire instance s'il n'existe pas
    instance_path = os.path.abspath(os.path.dirname(__file__))
    os.makedirs(os.path.join(instance_path, 'instance'), exist_ok=True)
    
    db_path = os.path.join(instance_path, 'instance', 'skillboard.db')
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
    }
    
    # ============================================================================
    # SÉCURITÉ
    # ============================================================================
    
    SECRET_KEY = os.getenv(
        'SECRET_KEY',
        'dev-key-change-in-production-asap'
    )
    
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = False  # Local, pas HTTPS
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
    # EMAIL
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
    
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    JSON_SORT_KEYS = False


class DevelopmentConfig(Config):
    """Configuration pour développement"""
    DEBUG = True
    TESTING = False
    SQLALCHEMY_ECHO = True


class ProductionConfig(Config):
    """Configuration pour production"""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Configuration pour tests"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    PROPAGATE_EXCEPTIONS = True  # Permet aux gestionnaires d'erreur de fonctionner


config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}