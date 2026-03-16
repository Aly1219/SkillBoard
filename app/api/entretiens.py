"""
Routes API pour les entretiens
"""
from flask_restx import Resource, Namespace
from app.models import Entretien
from app import db
from app.api.schemas import create_common_schemas
from app.db_helpers import get_entretien_by_id, get_poste_by_id

entretiens_ns = Namespace('entretiens', description='Gestion des entretiens')

# Créer les schémas pour ce namespace
schemas = create_common_schemas(entretiens_ns)


@entretiens_ns.route('')
class EntretienListAPI(Resource):
    @entretiens_ns.doc('list_entretiens', description='Récupérer tous les entretiens')
    @entretiens_ns.marshal_list_with(schemas['entretien_model'])
    @entretiens_ns.response(200, 'Liste des entretiens')
    def get(self):
        """
        Récupérer tous les entretiens
        
        Retourne la liste de tous les entretiens enregistrés.
        """
        return Entretien.query.all(), 200
    
    @entretiens_ns.doc('create_entretien', description='Créer un nouvel entretien')
    @entretiens_ns.expect(schemas['entretien_input'])
    @entretiens_ns.marshal_with(schemas['entretien_model'], code=201)
    @entretiens_ns.response(201, 'Entretien créé avec succès')
    @entretiens_ns.response(400, 'Données invalides')
    def post(self):
        """
        Créer un nouvel entretien
        
        Ajoute un nouvel entretien à la base de données.
        """
        data = entretiens_ns.payload
        
        if not data.get('candidat_nom'):
            return {'message': 'Le nom du candidat est requis'}, 400
        
        if not data.get('candidat_prenom'):
            return {'message': 'Le prénom du candidat est requis'}, 400
        
        if not data.get('date_entretien'):
            return {'message': 'La date de l\'entretien est requise'}, 400
        
        if not data.get('poste_id'):
            return {'message': 'L\'ID du poste est requis'}, 400
        
        poste = get_poste_by_id(data['poste_id'])
        if not poste:
            return {'message': 'Poste non trouvé'}, 400
        
        entretien = Entretien(
            candidat_nom=data['candidat_nom'],
            candidat_prenom=data['candidat_prenom'],
            date_entretien=data['date_entretien'],
            poste_id=data['poste_id'],
            recruteur_secondaire=data.get('recruteur_secondaire', ''),
        )
        db.session.add(entretien)
        db.session.commit()
        
        return entretien, 201


@entretiens_ns.route('/<int:id>')
@entretiens_ns.response(404, 'Entretien non trouvé')
@entretiens_ns.param('id', 'L\'ID de l\'entretien')
class EntretienAPI(Resource):
    @entretiens_ns.doc('get_entretien', description='Récupérer un entretien par ID')
    @entretiens_ns.marshal_with(schemas['entretien_model'])
    @entretiens_ns.response(200, 'Détails de l\'entretien')
    def get(self, id):
        """
        Récupérer un entretien par ID
        
        Retourne les détails d'un entretien spécifique.
        """
        entretien = get_entretien_by_id(id)
        
        if not entretien:
            return {'message': 'Entretien non trouvé'}, 404
        
        return entretien, 200
    
    @entretiens_ns.doc('update_entretien', description='Modifier un entretien')
    @entretiens_ns.expect(schemas['entretien_input'])
    @entretiens_ns.marshal_with(schemas['entretien_model'])
    @entretiens_ns.response(200, 'Entretien modifié')
    @entretiens_ns.response(404, 'Entretien non trouvé')
    def put(self, id):
        """
        Modifier un entretien
        
        Met à jour les informations d'un entretien.
        """
        entretien = get_entretien_by_id(id)
        
        if not entretien:
            return {'message': 'Entretien non trouvé'}, 404
        
        data = entretiens_ns.payload
        
        entretien.candidat_nom = data.get('candidat_nom', entretien.candidat_nom)
        entretien.candidat_prenom = data.get('candidat_prenom', entretien.candidat_prenom)
        entretien.date_entretien = data.get('date_entretien', entretien.date_entretien)
        entretien.recruteur_secondaire = data.get('recruteur_secondaire', entretien.recruteur_secondaire)
        
        if data.get('poste_id'):
            poste = get_poste_by_id(data['poste_id'])
            if not poste:
                return {'message': 'Poste non trouvé'}, 400
            entretien.poste_id = data['poste_id']
        
        db.session.commit()
        
        return entretien, 200
    
    @entretiens_ns.doc('delete_entretien', description='Supprimer un entretien')
    @entretiens_ns.response(200, 'Entretien supprimé')
    @entretiens_ns.response(404, 'Entretien non trouvé')
    def delete(self, id):
        """
        Supprimer un entretien
        
        Supprime un entretien de la base de données.
        """
        entretien = get_entretien_by_id(id)
        
        if not entretien:
            return {'message': 'Entretien non trouvé'}, 404
        
        db.session.delete(entretien)
        db.session.commit()
        
        return {'success': True, 'message': 'Entretien supprimé'}, 200