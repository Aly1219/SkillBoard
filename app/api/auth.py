"""
Routes d'authentification - API REST
"""
from flask import session, jsonify
from flask_restx import Resource, Namespace, fields
from werkzeug.security import check_password_hash
from app.models import User
from app import db

# Créer un namespace pour les routes auth
auth_ns = Namespace('auth', description='Authentification')

# Modèles pour Swagger
login_model = auth_ns.model('Login', {
    'username': fields.String(required=True, description='Nom d\'utilisateur'),
    'password': fields.String(required=True, description='Mot de passe'),
})

register_model = auth_ns.model('Register', {
    'username': fields.String(required=True, description='Nom d\'utilisateur'),
    'password': fields.String(required=True, description='Mot de passe'),
})

login_response = auth_ns.model('LoginResponse', {
    'success': fields.Boolean(description='Succès de la connexion'),
    'message': fields.String(description='Message de réponse'),
    'username': fields.String(description='Nom d\'utilisateur'),
})

@auth_ns.route('/login')
class LoginAPI(Resource):
    @auth_ns.doc('login_user', description='Connexion utilisateur')
    @auth_ns.expect(login_model)
    @auth_ns.marshal_with(login_response, code=200)
    @auth_ns.response(401, 'Identifiants invalides')
    def post(self):
        """
        Se connecter à l'application
        
        Permet à un utilisateur de se connecter avec ses identifiants.
        """
        data = auth_ns.payload
        user = User.query.filter_by(username=data['username']).first()
        
        if not user or not user.check_password(data['password']):
            return {'success': False, 'message': 'Identifiants invalides'}, 401
        
        session['user_id'] = user.id
        return {
            'success': True, 
            'message': 'Connecté avec succès',
            'username': user.username
        }, 200


@auth_ns.route('/register')
class RegisterAPI(Resource):
    @auth_ns.doc('register_user', description='Créer un nouvel utilisateur')
    @auth_ns.expect(register_model)
    @auth_ns.marshal_with(login_response, code=201)
    @auth_ns.response(409, 'Utilisateur existe déjà')
    def post(self):
        """
        Créer un nouvel utilisateur (Admin uniquement)
        
        Crée le compte administrateur (première utilisation uniquement).
        """
        data = auth_ns.payload
        
        if User.query.filter_by(username=data['username']).first():
            return {'success': False, 'message': 'Cet utilisateur existe déjà'}, 409
        
        user = User(username=data['username'])
        user.set_password(data['password'])
        db.session.add(user)
        db.session.commit()
        
        return {
            'success': True,
            'message': 'Utilisateur créé avec succès',
            'username': user.username
        }, 201


@auth_ns.route('/logout')
class LogoutAPI(Resource):
    @auth_ns.doc('logout_user', description='Déconnexion utilisateur')
    @auth_ns.response(200, 'Déconnexion réussie')
    def post(self):
        """
        Déconnecter l'utilisateur
        
        Termine la session utilisateur.
        """
        session.clear()
        return {'success': True, 'message': 'Déconnecté avec succès'}, 200