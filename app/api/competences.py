"""
Routes API pour les compétences
"""
from flask_restx import Resource, Namespace
from app.models import Competence
from app import db
from app.api.schemas import create_common_schemas
from app.db_helpers import get_competence_by_id, get_competence_by_name

competences_ns = Namespace('competences', description='Gestion des compétences')

# Créer les schémas pour ce namespace
schemas = create_common_schemas(competences_ns)


@competences_ns.route('')
class CompetenceListAPI(Resource):
    @competences_ns.doc('list_competences', description='Récupérer toutes les compétences')
    @competences_ns.marshal_list_with(schemas['competence_model'])
    @competences_ns.response(200, 'Liste des compétences récupérée')
    def get(self):
        """
        Récupérer toutes les compétences
        
        Retourne la liste complète des compétences disponibles.
        """
        return Competence.query.all(), 200
    
    @competences_ns.doc('create_competence', description='Créer une nouvelle compétence')
    @competences_ns.expect(schemas['competence_input'])
    @competences_ns.marshal_with(schemas['competence_model'], code=201)
    @competences_ns.response(201, 'Compétence créée avec succès')
    @competences_ns.response(400, 'Données invalides')
    def post(self):
        """
        Créer une nouvelle compétence
        
        Ajoute une nouvelle compétence à la base de données.
        """
        data = competences_ns.payload
        
        if not data.get('nom') or not data['nom'].strip():
            return {'message': 'Le nom est requis'}, 400
        
        if get_competence_by_name(data['nom']):
            return {'message': 'Cette compétence existe déjà'}, 400
        
        competence = Competence(nom=data['nom'])
        db.session.add(competence)
        db.session.commit()
        
        return competence, 201


@competences_ns.route('/<int:id>')
@competences_ns.response(404, 'Compétence non trouvée')
@competences_ns.param('id', 'L\'ID de la compétence')
class CompetenceAPI(Resource):
    @competences_ns.doc('get_competence', description='Récupérer une compétence par ID')
    @competences_ns.marshal_with(schemas['competence_model'])
    @competences_ns.response(200, 'Détails de la compétence')
    def get(self, id):
        """
        Récupérer une compétence par ID
        
        Retourne les détails d'une compétence spécifique.
        """
        competence = get_competence_by_id(id)
        
        if not competence:
            return {'message': 'Compétence non trouvée'}, 404
        
        return competence, 200
    
    @competences_ns.doc('update_competence', description='Modifier une compétence')
    @competences_ns.expect(schemas['competence_input'])
    @competences_ns.marshal_with(schemas['competence_model'])
    @competences_ns.response(200, 'Compétence modifiée')
    @competences_ns.response(404, 'Compétence non trouvée')
    def put(self, id):
        """
        Modifier une compétence
        
        Met à jour les informations d'une compétence.
        """
        competence = get_competence_by_id(id)
        
        if not competence:
            return {'message': 'Compétence non trouvée'}, 404
        
        data = competences_ns.payload
        
        if not data.get('nom') or not data['nom'].strip():
            return {'message': 'Le nom est requis'}, 400
        
        competence.nom = data['nom']
        db.session.commit()
        
        return competence, 200
    
    @competences_ns.doc('delete_competence', description='Supprimer une compétence')
    @competences_ns.response(200, 'Compétence supprimée')
    @competences_ns.response(404, 'Compétence non trouvée')
    def delete(self, id):
        """
        Supprimer une compétence
        
        Supprime une compétence de la base de données.
        """
        competence = get_competence_by_id(id)
        
        if not competence:
            return {'message': 'Compétence non trouvée'}, 404
        
        db.session.delete(competence)
        db.session.commit()
        
        return {'success': True, 'message': 'Compétence supprimée'}, 200