"""
Initialisation du module API REST avec Swagger
"""
from flask_restx import Api
from flask import Blueprint

# Créer un blueprint pour l'API
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')

# Créer l'API avec documentation Swagger
api = Api(
    api_bp,
    version='1.0',
    title='SkillBoard API',
    description='API REST formelle pour la gestion du recrutement',
    doc='/docs'  # URL pour accéder à la documentation Swagger
)

# Importer et enregistrer les namespaces après création de l'API
from app.api.auth import auth_ns
from app.api.competences import competences_ns
from app.api.entretiens import entretiens_ns
from app.api.voteGuest import guest_voting_ns

# Ajouter les namespaces
api.add_namespace(auth_ns, path='/auth')
api.add_namespace(competences_ns, path='/competences')
api.add_namespace(entretiens_ns, path='/entretiens')
api.add_namespace(guest_voting_ns, path='/voting')

__all__ = ['api_bp']