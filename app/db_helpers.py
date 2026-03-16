"""
Fonctions utilitaires pour les requêtes base de données
Applique le principe DRY pour éviter les répétitions
"""
from sqlalchemy import select
from app.extensions import db
from app.models import Poste, Competence, Entretien, User


def get_all_postes_sorted():
    """Récupère tous les postes triés par nom"""
    stmt = select(Poste).order_by(Poste.nom.asc())
    return db.session.scalars(stmt).all()


def get_all_competences_sorted():
    """Récupère toutes les compétences triées par nom"""
    stmt = select(Competence).order_by(Competence.nom.asc())
    return db.session.scalars(stmt).all()


def get_all_entretiens_sorted():
    """Récupère tous les entretiens triés par date"""
    stmt = select(Entretien).order_by(Entretien.date_entretien.asc())
    return db.session.scalars(stmt).all()


def get_dashboard_data():
    """Récupère toutes les données nécessaires pour le dashboard"""
    return {
        'postes': get_all_postes_sorted(),
        'all_competences': get_all_competences_sorted(),
        'entretiens': get_all_entretiens_sorted()
    }


def get_poste_by_id(poste_id):
    """Récupère un poste par ID, retourne None si inexistant"""
    return db.session.get(Poste, poste_id)


def get_competence_by_id(competence_id):
    """Récupère une compétence par ID"""
    return db.session.get(Competence, competence_id)


def get_entretien_by_id(entretien_id):
    """Récupère un entretien par ID"""
    return db.session.get(Entretien, entretien_id)


def get_poste_by_name(nom):
    """Récupère un poste par son nom"""
    stmt = select(Poste).where(Poste.nom == nom)
    return db.session.scalars(stmt).first()


def get_competence_by_name(nom):
    """Récupère une compétence par son nom"""
    stmt = select(Competence).where(Competence.nom == nom)
    return db.session.scalars(stmt).first()


def get_user_by_username(username):
    """Récupère un utilisateur par son nom d'utilisateur"""
    stmt = select(User).where(User.username == username)
    return db.session.scalars(stmt).first()


def user_exists():
    """Vérifie si au moins un utilisateur existe"""
    return User.query.first() is not None


def entretien_by_token(token):
    """Récupère un entretien par son token recruteur2"""
    stmt = select(Entretien).where(Entretien.token_recruteur2 == token)
    return db.session.scalars(stmt).first()