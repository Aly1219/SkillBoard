from app.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask import current_app
import jwt
import time

# Table d'association
poste_competence = db.Table('poste_competence',
    db.Column('poste_id', db.Integer, db.ForeignKey('poste.id'), primary_key=True),
    db.Column('competence_id', db.Integer, db.ForeignKey('competence.id'), primary_key=True)
)

class Competence(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)

class Poste(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    competences = db.relationship('Competence', secondary=poste_competence, lazy='subquery',
        backref=db.backref('postes', lazy=True))

class Entretien(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    candidat_nom = db.Column(db.String(50))
    candidat_prenom = db.Column(db.String(50))
    date_entretien = db.Column(db.String(20))
    recruteur_secondaire = db.Column(db.String(50))
    poste_id = db.Column(db.Integer, db.ForeignKey('poste.id'))
    poste = db.relationship('Poste', backref='entretiens')
    token_recruteur2 = db.Column(db.String(100), unique=True)
    statut = db.Column(db.String(20), default="Cree")
    evaluations = db.relationship('Evaluation', backref='entretien', lazy=True)

class Evaluation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    entretien_id = db.Column(db.Integer, db.ForeignKey('entretien.id'), nullable=False)
    competence_id = db.Column(db.Integer, db.ForeignKey('competence.id'), nullable=False)
    note_rh = db.Column(db.Integer, nullable=True)
    note_recruteur2 = db.Column(db.Integer, nullable=True)
    competence = db.relationship('Competence')

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def get_reset_token(self, expires_sec=1800):
        """Génère un token valide 30 minutes (1800 sec)"""
        payload = {
            'user_id': self.id,
            'exp': time.time() + expires_sec
        }
        return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')
    
    @staticmethod
    def verify_reset_token(token):
        """Vérifie le token et retourne l'user associé"""
        try:
            payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            user_id = payload['user_id']
            return User.query.get(user_id)
        except:
            return None

    def set_password(self, password):
        """Crée le hash du mot de passe"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Vérifie le mot de passe hashé"""
        return check_password_hash(self.password_hash, password)