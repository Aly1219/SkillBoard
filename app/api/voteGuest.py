"""
Routes API pour le blind-voting du 2e recruteur
Permet à un 2e recruteur d'évaluer un candidat sans voir les notes du RH
"""
from flask_restx import Resource, Namespace, fields
from app.models import Entretien, Evaluation
from app import db

# Namespace dédié au voting
guest_voting_ns = Namespace('voting', description='Blind voting du 2e recruteur')

# Modèles Swagger
competence_for_voting = guest_voting_ns.model('CompetenceForVoting', {
    'id': fields.Integer(readonly=True, description='ID de la compétence'),
    'nom': fields.String(description='Nom de la compétence'),
    'palier': fields.Integer(description='Palier minimum attendu'),
    'ponderations': fields.Integer(description='Pondération de la compétence'),
})

interview_voting_model = guest_voting_ns.model('InterviewForVoting', {
    'id': fields.Integer(readonly=True, description='ID de l\'entretien'),
    'candidat_nom': fields.String(description='Nom du candidat'),
    'candidat_prenom': fields.String(description='Prénom du candidat'),
    'candidat_complet': fields.String(description='Nom complet du candidat'),
    'date_entretien': fields.String(description='Date de l\'entretien'),
    'poste_nom': fields.String(description='Nom du poste'),
    'competences': fields.List(fields.Nested(competence_for_voting), description='Compétences à évaluer'),
    'recruteur_rh': fields.String(description='Nom du RH'),
    'recruteur_secondaire': fields.String(description='Nom du 2e recruteur'),
})

vote_input = guest_voting_ns.model('VoteInput', {
    'evaluations': fields.List(
        fields.Nested(guest_voting_ns.model('EvaluationInput', {
            'competence_id': fields.Integer(required=True, description='ID de la compétence'),
            'note': fields.Integer(required=True, description='Note (1-10)')
        })),
        required=True,
        description='Liste des évaluations'
    )
})

vote_response = guest_voting_ns.model('VoteResponse', {
    'success': fields.Boolean(description='Succès de l\'opération'),
    'message': fields.String(description='Message de confirmation'),
    'entretien_id': fields.Integer(description='ID de l\'entretien votée'),
})


@guest_voting_ns.route('/interview/<token>')
@guest_voting_ns.param('token', 'Token d\'accès au voting')
class GuestVotingGetAPI(Resource):
    @guest_voting_ns.doc('get_interview_for_voting', description='Récupérer les données d\'un entretien pour le blind voting')
    @guest_voting_ns.response(200, 'Données de l\'entretien (SANS notes RH)', interview_voting_model)
    @guest_voting_ns.response(404, 'Token invalide ou entretien non trouvé')
    @guest_voting_ns.response(400, 'Entretien déjà complété')
    def get(self, token):
        """
        Récupérer les données d'un entretien pour blind voting
        
        Retourne les infos du candidat et les compétences à évaluer
        SANS afficher les notes du RH (blind voting).
        
        Le token doit être valide et l'entretien doit être en attente du 2e recruteur.
        """
        # 1. Vérifier le token
        entretien = Entretien.query.filter_by(token_recruteur2=token).first()
        if not entretien:
            return {
                'message': 'Entretien non trouvé ou token invalide'
            }, 404
        
        # 2. Vérifier le statut
        if entretien.statut == "Termine":
            return {
                'message': 'Cet entretien est terminé. Le vote a déjà été enregistré.'
            }, 400
        
        if entretien.statut != "Attente_Recruteur2":
            return {
                'message': f'Cet entretien n\'est pas en attente d\'évaluation (statut: {entretien.statut})'
            }, 400
        
        # 3. Construire la réponse (SANS les notes du RH)
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
            'recruteur_rh': None,  # On ne montre pas qui a voté
            'recruteur_secondaire': entretien.recruteur_secondaire
        }, 200


@guest_voting_ns.route('/interview/<token>/submit-votes')
@guest_voting_ns.param('token', 'Token d\'accès au voting')
class GuestVotingSubmitAPI(Resource):
    @guest_voting_ns.doc('submit_guest_votes', description='Soumettre les votes du 2e recruteur')
    @guest_voting_ns.expect(vote_input)
    @guest_voting_ns.marshal_with(vote_response, code=200)
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
        # 1. Vérifier le token
        entretien = Entretien.query.filter_by(token_recruteur2=token).first()
        if not entretien:
            return {
                'success': False,
                'message': 'Token invalide ou expiré'
            }, 401
        
        # 2. Vérifier que l'entretien est en attente
        if entretien.statut == "Termine":
            return {
                'success': False,
                'message': 'Ce vote a déjà été enregistré'
            }, 409
        
        if entretien.statut != "Attente_Recruteur2":
            return {
                'success': False,
                'message': f'Cet entretien n\'est pas en attente d\'évaluation'
            }, 400
        
        # 3. Récupérer les votes
        try:
            data = guest_voting_ns.payload
            evaluations = data.get('evaluations', [])
            
            if not evaluations:
                return {
                    'success': False,
                    'message': 'Au moins une évaluation est requise'
                }, 400
            
            # 4. Valider et enregistrer chaque vote
            for eval_data in evaluations:
                competence_id = eval_data.get('competence_id')
                note = eval_data.get('note')
                
                # Valider la note
                if not isinstance(note, int) or note < 1 or note > 10:
                    return {
                        'success': False,
                        'message': f'Les notes doivent être des entiers entre 1 et 10. Reçu: {note}'
                    }, 400
                
                # Trouver l'évaluation
                evaluation = Evaluation.query.filter_by(
                    entretien_id=entretien.id,
                    competence_id=competence_id
                ).first()
                
                if not evaluation:
                    return {
                        'success': False,
                        'message': f'Compétence ID {competence_id} introuvable pour cet entretien'
                    }, 400
                
                # Enregistrer la note du 2e recruteur
                evaluation.note_recruteur2 = note
            
            # 5. Marquer comme terminé et invalider le token
            entretien.statut = "Termine"
            entretien.token_recruteur2 = None
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