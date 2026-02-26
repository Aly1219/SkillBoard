"""
Routes API pour les entretiens
"""
from flask_restx import Resource, Namespace, fields
from datetime import datetime
from app.models import Entretien, Evaluation
from app import db

entretiens_ns = Namespace('entretiens', description='Gestion des entretiens')

# Modèles pour Swagger
entretien_model = entretiens_ns.model('Entretien', {
    'id': fields.Integer(readonly=True, description='ID de l\'entretien'),
    'candidat_nom': fields.String(required=True, description='Nom du candidat'),
    'candidat_prenom': fields.String(required=True, description='Prénom du candidat'),
    'date_entretien': fields.String(required=True, description='Date de l\'entretien (YYYY-MM-DD)'),
    'poste_id': fields.Integer(required=True, description='ID du poste'),
    'recruteur_secondaire': fields.String(description='Nom du 2e recruteur'),
    'statut': fields.String(description='Statut (Cree, Attente_RH, Attente_Recruteur2, Termine)'),
})

entretien_input = entretiens_ns.model('EntretienInput', {
    'candidat_nom': fields.String(required=True, description='Nom du candidat'),
    'candidat_prenom': fields.String(required=True, description='Prénom du candidat'),
    'date_entretien': fields.String(required=True, description='Date (YYYY-MM-DD)'),
    'poste_id': fields.Integer(required=True, description='ID du poste'),
    'recruteur_secondaire': fields.String(description='Nom du 2e recruteur'),
})

evaluation_model = entretiens_ns.model('Evaluation', {
    'id': fields.Integer(readonly=True, description='ID de l\'évaluation'),
    'competence_id': fields.Integer(required=True, description='ID de la compétence'),
    'note_rh': fields.Integer(description='Note du RH (1-10)'),
    'note_recruteur2': fields.Integer(description='Note du 2e recruteur (1-10)'),
})


@entretiens_ns.route('')
class EntretienListAPI(Resource):
    @entretiens_ns.doc('list_entretiens', description='Récupérer tous les entretiens')
    @entretiens_ns.marshal_list_with(entretien_model)
    @entretiens_ns.response(200, 'Liste des entretiens')
    def get(self):
        """
        Récupérer tous les entretiens
        
        Retourne la liste de tous les entretiens enregistrés.
        """
        return Entretien.query.all(), 200
    
    @entretiens_ns.doc('create_entretien', description='Créer un nouvel entretien')
    @entretiens_ns.expect(entretien_input)
    @entretiens_ns.marshal_with(entretien_model, code=201)
    @entretiens_ns.response(201, 'Entretien créé avec succès')
    def post(self):
        """
        Créer un nouvel entretien
        
        Ajoute un nouvel entretien à la base de données.
        """
        data = entretiens_ns.payload
        
        entretien = Entretien(
            candidat_nom=data['candidat_nom'],
            candidat_prenom=data['candidat_prenom'],
            date_entretien=data['date_entretien'],
            poste_id=data['poste_id'],
            recruteur_secondaire=data.get('recruteur_secondaire', ''),
            statut='Cree'
        )
        db.session.add(entretien)
        db.session.flush()
        
        # Créer les évaluations vides pour chaque compétence du poste
        poste = entretien.poste
        if poste:
            for competence in poste.competences:
                evaluation = Evaluation(
                    entretien_id=entretien.id,
                    competence_id=competence.id,
                )
                db.session.add(evaluation)
        
        db.session.commit()
        return entretien, 201


@entretiens_ns.route('/<int:id>')
@entretiens_ns.param('id', 'L\'ID de l\'entretien')
class EntretienAPI(Resource):
    @entretiens_ns.doc('get_entretien', description='Récupérer un entretien par ID')
    @entretiens_ns.marshal_with(entretien_model)
    @entretiens_ns.response(200, 'Détails de l\'entretien')
    @entretiens_ns.response(404, 'Entretien non trouvé')
    def get(self, id):
        """
        Récupérer un entretien par ID
        
        Retourne les détails d'un entretien spécifique avec ses évaluations.
        """
        entretien = Entretien.query.get_or_404(id)
        return entretien, 200
    
    @entretiens_ns.doc('update_entretien', description='Modifier un entretien')
    @entretiens_ns.expect(entretien_input)
    @entretiens_ns.marshal_with(entretien_model)
    @entretiens_ns.response(200, 'Entretien modifié')
    def put(self, id):
        """
        Modifier un entretien
        
        Met à jour les informations d'un entretien.
        """
        entretien = Entretien.query.get_or_404(id)
        data = entretiens_ns.payload
        
        entretien.candidat_nom = data.get('candidat_nom', entretien.candidat_nom)
        entretien.candidat_prenom = data.get('candidat_prenom', entretien.candidat_prenom)
        entretien.date_entretien = data.get('date_entretien', entretien.date_entretien)
        
        db.session.commit()
        return entretien, 200
    
    @entretiens_ns.doc('delete_entretien', description='Supprimer un entretien')
    @entretiens_ns.response(204, 'Entretien supprimé')
    @entretiens_ns.response(404, 'Entretien non trouvé')
    def delete(self, id):
        """
        Supprimer un entretien
        
        Supprime un entretien et ses évaluations associées.
        """
        entretien = Entretien.query.get_or_404(id)
        db.session.delete(entretien)
        db.session.commit()
        
        return '', 204


@entretiens_ns.route('/<int:id>/evaluations')
@entretiens_ns.param('id', 'L\'ID de l\'entretien')
class EvaluationListAPI(Resource):
    @entretiens_ns.doc('list_evaluations', description='Récupérer les évaluations d\'un entretien')
    @entretiens_ns.marshal_list_with(evaluation_model)
    @entretiens_ns.response(200, 'Liste des évaluations')
    def get(self, id):
        """
        Récupérer les évaluations d'un entretien
        
        Retourne toutes les évaluations associées à un entretien.
        """
        evaluations = Evaluation.query.filter_by(entretien_id=id).all()
        return evaluations, 200