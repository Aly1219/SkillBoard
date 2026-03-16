"""
Routes API pour le blind-voting du 2e recruteur
Permet à un 2e recruteur d'évaluer un candidat sans voir les notes du RH
"""
from flask_restx import Resource, Namespace
from app.models import Entretien, Evaluation
from app import db
from app.api.schemas import create_common_schemas
from app.db_helpers import entretien_by_token

# Namespace dédié au voting
guest_voting_ns = Namespace('voting', description='Blind voting du 2e recruteur')

# Créer les schémas pour ce namespace
schemas = create_common_schemas(guest_voting_ns)


@guest_voting_ns.route('/interview/<token>')
@guest_voting_ns.param('token', 'Token d\'accès au voting')
class GuestVotingGetAPI(Resource):
    @guest_voting_ns.doc('get_interview_for_voting', description='Récupérer les données d\'un entretien pour le blind voting')
    @guest_voting_ns.response(200, 'Données de l\'entretien (SANS notes RH)', schemas['interview_voting_model'])
    @guest_voting_ns.response(404, 'Token invalide ou entretien non trouvé')
    @guest_voting_ns.response(400, 'Entretien déjà complété')
    def get(self, token):
        """
        Récupérer les données d'un entretien pour blind voting
        
        Retourne les infos du candidat et les compétences à évaluer
        SANS afficher les notes du RH (blind voting).
        
        Le token doit être valide et l'entretien doit être en attente du 2e recruteur.
        """
        entretien = entretien_by_token(token)
        
        if not entretien:
            return {'message': 'Entretien non trouvé ou token invalide'}, 404
        
        if entretien.statut == "Termine":
            return {'message': 'Cet entretien est terminé. Le vote a déjà été enregistré.'}, 400
        
        if entretien.statut != "Attente_Recruteur2":
            return {'message': f'Cet entretien n\'est pas en attente d\'évaluation (statut: {entretien.statut})'}, 400
        
        # Construire la réponse (SANS les notes du RH)
        competences_data = []
        for eval in entretien.evaluations:
            competences_data.append({
                'id': eval.competence.id,
                'nom': eval.competence.nom,
                'palier': getattr(eval, 'palier', None),
                'ponderations': getattr(eval, 'ponderations', None)
            })
        
        return {
            'id': entretien.id,
            'candidat_nom': entretien.candidat_nom,
            'candidat_prenom': entretien.candidat_prenom,
            'candidat_complet': f"{entretien.candidat_prenom} {entretien.candidat_nom}",
            'date_entretien': entretien.date_entretien,
            'poste_nom': entretien.poste.nom if entretien.poste else None,
            'competences': competences_data,
            'recruteur_rh': None,
            'recruteur_secondaire': entretien.recruteur_secondaire
        }, 200


@guest_voting_ns.route('/interview/<token>/submit-votes')
@guest_voting_ns.param('token', 'Token d\'accès au voting')
class GuestVotingSubmitAPI(Resource):
    @guest_voting_ns.doc('submit_guest_votes', description='Soumettre les votes du 2e recruteur')
    @guest_voting_ns.expect(schemas['vote_input'])
    @guest_voting_ns.marshal_with(schemas['vote_response'], code=200)
    @guest_voting_ns.response(400, 'Données invalides ou notes hors limites')
    @guest_voting_ns.response(401, 'Token invalide ou expiré')
    @guest_voting_ns.response(409, 'Vote déjà enregistré')
    def post(self, token):
        """
        Soumettre les votes du 2e recruteur
        
        Enregistre les évaluations du 2e recruteur pour chaque compétence.
        Marque l'entretien comme "Termine" et invalide le token.
        
        Les notes doivent être entre 1 et 10.
        """
        entretien = entretien_by_token(token)
        
        if not entretien:
            return {
                'success': False,
                'message': 'Entretien non trouvé ou token invalide'
            }, 401
        
        if entretien.statut == "Termine":
            return {'success': False, 'message': 'Ce vote a déjà été enregistré'}, 409
        
        if entretien.statut != "Attente_Recruteur2":
            return {'success': False, 'message': f'Cet entretien n\'est pas en attente d\'évaluation (statut: {entretien.statut})'}, 400
        
        # Traiter les votes
        data = guest_voting_ns.payload
        
        if not data.get('evaluations'):
            return {
                'success': False,
                'message': 'Aucune évaluation fournie'
            }, 400
        
        for vote_data in data['evaluations']:
            competence_id = vote_data.get('competence_id')
            note = vote_data.get('note')
            
            # Valider la note
            try:
                note_int = int(note)
                if note_int < 1 or note_int > 10:
                    return {'success': False, 'message': f'La note doit être entre 1 et 10'}, 400
            except (ValueError, TypeError):
                return {'success': False, 'message': 'La note doit être un nombre'}, 400
            
            # Trouver l'évaluation correspondante
            evaluation = Evaluation.query.filter_by(
                entretien_id=entretien.id,
                competence_id=competence_id
            ).first()
            
            if evaluation:
                evaluation.note_recruteur2 = int(note)
        
        # Marquer comme terminé et invalider le token
        entretien.statut = "Termine"
        entretien.token_recruteur2 = None
        
        try:
            db.session.commit()
            return {
                'success': True,
                'message': 'Votes enregistrés avec succès',
                'entretien_id': entretien.id
            }, 200
        except Exception as e:
            db.session.rollback()
            return {
                'success': False,
                'message': f'Erreur lors de l\'enregistrement: {str(e)}'
            }, 400