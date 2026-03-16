"""
Schémas Swagger centralisés pour l'API REST
Évite la duplication de code entre les différents namespaces
"""
from flask_restx import fields


def create_common_schemas(ns):
    """
    Crée et retourne tous les schémas communs pour un namespace donné
    
    Args:
        ns: Le namespace Flask-RESTX
    
    Returns:
        dict: Dictionnaire avec tous les modèles
    """
    
    schemas = {}
    
    # ========== MODÈLES AUTHENTIFICATION ==========
    schemas['login_model'] = ns.model('Login', {
        'username': fields.String(required=True, description='Nom d\'utilisateur'),
        'password': fields.String(required=True, description='Mot de passe'),
    })

    schemas['register_model'] = ns.model('Register', {
        'username': fields.String(required=True, description='Nom d\'utilisateur'),
        'password': fields.String(required=True, description='Mot de passe'),
    })

    schemas['login_response'] = ns.model('LoginResponse', {
        'success': fields.Boolean(description='Succès de la connexion'),
        'message': fields.String(description='Message de réponse'),
        'username': fields.String(description='Nom d\'utilisateur'),
    })

    # ========== MODÈLES COMPÉTENCES ==========
    schemas['competence_model'] = ns.model('Competence', {
        'id': fields.Integer(readonly=True, description='ID de la compétence'),
        'nom': fields.String(required=True, description='Nom de la compétence'),
    })

    schemas['competence_input'] = ns.model('CompetenceInput', {
        'nom': fields.String(required=True, description='Nom de la compétence'),
    })

    # ========== MODÈLES POSTES ==========
    schemas['poste_model'] = ns.model('Poste', {
        'id': fields.Integer(readonly=True, description='ID du poste'),
        'nom': fields.String(required=True, description='Nom du poste'),
    })

    schemas['poste_input'] = ns.model('PosteInput', {
        'nom': fields.String(required=True, description='Nom du poste'),
    })

    # ========== MODÈLES ENTRETIENS ==========
    schemas['entretien_model'] = ns.model('Entretien', {
        'id': fields.Integer(readonly=True, description='ID de l\'entretien'),
        'candidat_nom': fields.String(required=True, description='Nom du candidat'),
        'candidat_prenom': fields.String(required=True, description='Prénom du candidat'),
        'date_entretien': fields.String(required=True, description='Date de l\'entretien (YYYY-MM-DD)'),
        'poste_id': fields.Integer(required=True, description='ID du poste'),
        'recruteur_secondaire': fields.String(description='Nom du 2e recruteur'),
        'statut': fields.String(description='Statut'),
    })

    schemas['entretien_input'] = ns.model('EntretienInput', {
        'candidat_nom': fields.String(required=True, description='Nom du candidat'),
        'candidat_prenom': fields.String(required=True, description='Prénom du candidat'),
        'date_entretien': fields.String(required=True, description='Date (YYYY-MM-DD)'),
        'poste_id': fields.Integer(required=True, description='ID du poste'),
        'recruteur_secondaire': fields.String(description='Nom du 2e recruteur'),
    })

    # ========== MODÈLES ÉVALUATIONS ==========
    schemas['evaluation_model'] = ns.model('Evaluation', {
        'id': fields.Integer(readonly=True, description='ID de l\'évaluation'),
        'competence_id': fields.Integer(required=True, description='ID de la compétence'),
        'note_rh': fields.Integer(description='Note du RH (1-10)'),
        'note_recruteur2': fields.Integer(description='Note du 2e recruteur (1-10)'),
    })

    schemas['evaluation_input'] = ns.model('EvaluationInput', {
        'competence_id': fields.Integer(required=True, description='ID de la compétence'),
        'note': fields.Integer(required=True, description='Note (1-10)'),
    })

    # ========== MODÈLES VOTING ==========
    schemas['competence_for_voting'] = ns.model('CompetenceForVoting', {
        'id': fields.Integer(readonly=True, description='ID de la compétence'),
        'nom': fields.String(description='Nom de la compétence'),
        'palier': fields.Integer(description='Palier minimum attendu'),
        'ponderations': fields.Integer(description='Pondération de la compétence'),
    })

    schemas['interview_voting_model'] = ns.model('InterviewForVoting', {
        'id': fields.Integer(readonly=True, description='ID de l\'entretien'),
        'candidat_nom': fields.String(description='Nom du candidat'),
        'candidat_prenom': fields.String(description='Prénom du candidat'),
        'candidat_complet': fields.String(description='Nom complet du candidat'),
        'date_entretien': fields.String(description='Date de l\'entretien'),
        'poste_nom': fields.String(description='Nom du poste'),
        'competences': fields.List(fields.Nested(schemas['competence_for_voting']), description='Compétences à évaluer'),
        'recruteur_rh': fields.String(description='Nom du RH'),
        'recruteur_secondaire': fields.String(description='Nom du 2e recruteur'),
    })

    schemas['vote_input'] = ns.model('VoteInput', {
        'evaluations': fields.List(
            fields.Nested(schemas['evaluation_input']),
            required=True,
            description='Liste des évaluations'
        )
    })

    schemas['vote_response'] = ns.model('VoteResponse', {
        'success': fields.Boolean(description='Succès de l\'opération'),
        'message': fields.String(description='Message de confirmation'),
        'entretien_id': fields.Integer(description='ID de l\'entretien votée'),
    })
    
    return schemas