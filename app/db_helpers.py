"""
Fonctions utilitaires pour les requêtes base de données.
Centralise toutes les requêtes pour respecter le principe DRY
et garder les routes propres de tout accès direct à la base.
"""

# ============================================================
# TABLE DES MATIÈRES
# 1.  POSTES        get_all / get_by_id / get_by_name
# 2.  COMPÉTENCES   get_all / get_by_id / get_by_name
# 3.  ENTRETIENS    get_all / get_by_id
# 4.  UTILISATEURS  get_by_username / user_exists
# ============================================================

from sqlalchemy import select
from app.extensions import db
from app.models import Poste, Competence, Entretien, User


# ============================================================
# 1. POSTES
# ============================================================

def get_all_postes_sorted():
    """Récupère tous les postes triés par nom"""
    return db.session.scalars(select(Poste).order_by(Poste.nom.asc())).all()


def get_poste_by_id(poste_id):
    """Récupère un poste par ID, retourne None si inexistant"""
    return db.session.get(Poste, poste_id)


def get_poste_by_name(nom):
    """Récupère un poste par son nom exact"""
    return db.session.scalars(select(Poste).where(Poste.nom == nom)).first()


# ============================================================
# 2. COMPÉTENCES
# ============================================================

def get_all_competences_sorted():
    """Récupère toutes les compétences triées par nom"""
    return db.session.scalars(select(Competence).order_by(Competence.nom.asc())).all()


def get_competence_by_id(competence_id):
    """Récupère une compétence par ID"""
    return db.session.get(Competence, competence_id)


def get_competence_by_name(nom):
    """Récupère une compétence par son nom exact"""
    return db.session.scalars(select(Competence).where(Competence.nom == nom)).first()


# ============================================================
# 3. ENTRETIENS
# ============================================================

def get_all_entretiens_sorted():
    """Récupère tous les entretiens triés par date"""
    return db.session.scalars(select(Entretien).order_by(Entretien.date_entretien.asc())).all()


def get_entretien_by_id(entretien_id):
    """Récupère un entretien par ID"""
    return db.session.get(Entretien, entretien_id)


def get_dashboard_data():
    """Récupère toutes les données nécessaires pour le dashboard en un seul appel"""
    return {
        'postes':           get_all_postes_sorted(),
        'all_competences':  get_all_competences_sorted(),
        'entretiens':       get_all_entretiens_sorted(),
    }


# ============================================================
# 4. UTILISATEURS
# ============================================================

def get_user_by_username(username):
    """Récupère un utilisateur par son nom d'utilisateur"""
    return db.session.scalars(select(User).where(User.username == username)).first()


def user_exists():
    """Vérifie si au moins un utilisateur existe en base"""
    return db.session.scalars(select(User)).first() is not None