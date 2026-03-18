import os
from datetime import timedelta

# ============================================================
# TABLE DES MATIÈRES
# 1.  Config de base
# 2.  DevelopmentConfig
# 3.  ProductionConfig
# 4.  TestingConfig
# 5.  config_by_name
# ============================================================


class Config:
    """Configuration de base pour SkillBoard"""

    # ============================================================
    # BASE DE DONNÉES
    # ============================================================

    # Le répertoire instance est créé dans create_app(), pas ici
    instance_path = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(instance_path, 'instance', 'skillboard.db')
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{db_path}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Note : pool_size et pool_recycle ne sont pas supportés par SQLite.
    # Ces options sont réservées à PostgreSQL/MySQL en production.
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,  # Seule option compatible SQLite
    }

    # ============================================================
    # SÉCURITÉ
    # ============================================================

    SECRET_KEY = os.getenv(
        'SECRET_KEY',
        'dev-key-change-in-production-asap'
    )

    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = False  # Passer à True en production avec HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # ============================================================
    # FLASK
    # ============================================================

    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    TESTING = False

    # ============================================================
    # CACHE
    # ============================================================

    CACHE_TYPE = os.getenv('CACHE_TYPE', 'SimpleCache')
    CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_DEFAULT_TIMEOUT', '3600'))

    # ============================================================
    # EMAIL
    # ============================================================

    MAIL_SERVER          = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT            = int(os.getenv('MAIL_PORT', '587'))
    MAIL_USE_TLS         = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME        = os.getenv('MAIL_USERNAME', '')
    MAIL_PASSWORD        = os.getenv('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER  = os.getenv('MAIL_DEFAULT_SENDER', 'noreply@skillboard.com')

    # ============================================================
    # LOGGING
    # ============================================================

    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE  = os.getenv('LOG_FILE', 'skillboard.log')

    # ============================================================
    # APPLICATION
    # ============================================================

    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB
    JSON_SORT_KEYS = False


# ============================================================
# 2. DÉVELOPPEMENT
# ============================================================
class DevelopmentConfig(Config):
    """Configuration pour le développement local"""
    ENV   = 'development'
    DEBUG = True


# ============================================================
# 3. PRODUCTION
# ============================================================
class ProductionConfig(Config):
    """Configuration pour la production"""
    ENV   = 'production'
    DEBUG = False
    # En production : passer SESSION_COOKIE_SECURE = True
    # et fournir SECRET_KEY via variable d'environnement


# ============================================================
# 4. TESTS
# ============================================================
class TestingConfig(Config):
    """Configuration pour les tests automatisés"""
    ENV                     = 'testing'
    TESTING                 = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED        = False
    PROPAGATE_EXCEPTIONS    = False  # Laisse les gestionnaires d'erreur s'activer


# ============================================================
# 5. SÉLECTEUR
# ============================================================
config_by_name = {
    'development': DevelopmentConfig,
    'production':  ProductionConfig,
    'testing':     TestingConfig,
    'default':     DevelopmentConfig,
}