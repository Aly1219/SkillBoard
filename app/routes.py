from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, send_file, abort
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db, cache
from app.models import User, Poste, Competence, Entretien, Evaluation
from datetime import datetime
from sqlalchemy import select, delete
import uuid
import app.calculs as calculs
from app.db_helpers import (
    get_dashboard_data,
    get_poste_by_id,
    get_poste_by_name,
    get_competence_by_id,
    get_competence_by_name,
    get_entretien_by_id,
    get_user_by_username,
    user_exists,
    entretien_by_token,
    get_all_competences_sorted
)
from app.validators import (
    validate_string_field,
    validate_skill_exists,
    validate_poste_exists,
    validate_entretien_exists,
    validate_entretien_not_finished,
    validate_entretien_waiting_for_recruiter2,
    validate_note_range
)

# On définit un blueprint nommé 'main'
bp = Blueprint('main', __name__)

# --- ROUTE D'ACCUEIL (DASHBOARD) ---
@bp.route('/')
@login_required
def home():
    """Affiche le dashboard avec toutes les données"""
    from app.db_helpers import get_dashboard_data
    
    data = get_dashboard_data()
    
    return render_template('index.html', 
                           user=current_user.username,
                           jobs=data['postes'],
                           all_skills=data['all_competences'],
                           entretiens=data['entretiens'])

# --- ROUTE LOGIN ---
@bp.route('/login', methods=['GET', 'POST'])
def login():
    from app.db_helpers import user_exists, get_user_by_username
    
    # Si l'utilisateur est déjà connecté, on l'envoie au dashboard
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    # LOGIQUE (1) - Première connexion
    # Si aucun utilisateur n'existe dans la base, on force la redirection vers l'inscription
    if not user_exists():
        return redirect(url_for('main.register'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = get_user_by_username(username)

        # Vérification du mot de passe
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('main.home'))
        else:
            flash('Nom d\'utilisateur ou mot de passe incorrect')
    return render_template('login.html')

# --- ROUTE INSCRIPTION ---
@bp.route('/register', methods=['GET', 'POST'])
def register():
    from app.db_helpers import user_exists
    
    # Sécurité : Si un utilisateur existe déjà, on empêche d'en créer un nouveau
    if user_exists() and not current_user.is_authenticated:
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Création du nouvel utilisateur
        new_user = User(username=username)
        new_user.set_password(password)
        
        db.session.add(new_user)
        db.session.commit()
        
        # On connecte directement l'utilisateur après l'inscription
        login_user(new_user)
        return redirect(url_for('main.home'))

    return render_template('register.html')

# --- ROUTE LOGOUT ---
@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

# --- ROUTE POSTES EXISTANTS ---
@bp.route('/api/poste/<int:poste_id>')
def get_poste_details(poste_id):
    from app.db_helpers import get_poste_by_id

    poste = get_poste_by_id(poste_id)
    if not poste:
        abort(404)
    skills = [{"id": c.id, "nom": c.nom} for c in poste.competences]
    return jsonify({
        "nom": poste.nom,
        "competences": skills
    })

# --- ROUTE AJOUTER POSTE ---
@bp.route('/add_poste', methods=['POST'])
def add_poste():
    from app.db_helpers import get_competence_by_id
    
    nom = request.form.get('nom_poste')
    skill_ids = request.form.getlist('competences')
    
    if nom:
        nouveau_poste = Poste(nom=nom)
        db.session.add(nouveau_poste)
        db.session.flush()

        for s_id in skill_ids:
            comp = get_competence_by_id(s_id)
            if comp:
                nouveau_poste.competences.append(comp)
        
        db.session.commit()
        
    return redirect(url_for('main.home'))

# --- ROUTE MODIFIER UN POSTE ---
@bp.route('/update_poste', methods=['POST'])
def update_poste():
    from app.db_helpers import get_poste_by_id, get_competence_by_id
    
    # 1. Récupération des données du formulaire
    poste_id = request.form.get('poste_id')
    nom_poste = request.form.get('nom_poste')
    competences_ids = request.form.getlist('competences') 

    # 2. Recherche du poste dans la base de données
    poste = get_poste_by_id(poste_id)

    if poste:
        # 3. Mise à jour du nom
        poste.nom = nom_poste

        # 4. Mise à jour des compétences
        nouvelle_liste_competences = []
        for skill_id in competences_ids:
            skill = get_competence_by_id(int(skill_id))
            if skill:
                nouvelle_liste_competences.append(skill)
        poste.competences = nouvelle_liste_competences

        # 5. Sauvegarde en base
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Erreur lors de la mise à jour : {e}")

    return redirect(url_for('main.home'))

# --- ROUTE SUPPRIMER UN POSTE ---
@bp.route('/api/poste/<int:poste_id>', methods=['DELETE'])
def api_delete_poste(poste_id):
    from app.db_helpers import get_poste_by_id
    
    poste = get_poste_by_id(poste_id)
    if not poste:
        return jsonify({'success': False, 'message': 'Poste non trouvé'}), 404

    try:
        db.session.delete(poste)
        db.session.commit()
        return jsonify({
            'success': True, 
            'message': 'Poste supprimé', 
            'poste': {'id': poste.id, 'nom': poste.nom}
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Erreur serveur'}), 500

# --- ROUTE AJOUTER COMPETENCE ---
@bp.route('/add_competence', methods=['POST'])
@login_required
def add_competence():
    from app.db_helpers import get_competence_by_name
    
    nom = request.form.get('nom_competence')
    
    if nom:
        # On vérifie si la compétence existe déjà pour éviter les doublons
        existe = get_competence_by_name(nom)
        
        if not existe:
            nouvelle_comp = Competence(nom=nom)
            db.session.add(nouvelle_comp)
            db.session.commit()
            
    return redirect(url_for('main.home'))

# --- ROUTE TRAITEMENT DU FORMULAIRE DE CREATION D'ENTRETIEN ---
@bp.route('/create_interview', methods=['POST'])
def create_interview():
    from app.db_helpers import get_poste_by_name
    
    # Récupération des données du formulaire
    nom = request.form.get('cand_nom')
    prenom = request.form.get('cand_prenom')
    date = request.form.get('entr_date')
    recruteur2 = request.form.get('entr_recruteur')
    poste_nom = request.form.get('entr_poste')
    
    # Trouver le poste correspondant (pour lier les compétences)
    poste = get_poste_by_name(poste_nom)
    
    if poste:
        nouvel_entretien = Entretien(
            candidat_nom=nom,
            candidat_prenom=prenom,
            date_entretien=date,
            recruteur_secondaire=recruteur2,
            poste=poste
        )
        db.session.add(nouvel_entretien)
        db.session.flush()
        # 2. SNAPSHOT : On crée immédiatement les lignes d'évaluation vides
        # Ainsi, si le poste change demain, cet entretien garde CES compétences-là.
        for competence in poste.competences:
            nouvelle_eval = Evaluation(
                entretien_id=nouvel_entretien.id,
                competence_id=competence.id,
            )
            db.session.add(nouvelle_eval)
        db.session.commit()
        
        # Redirection vers la nouvelle page avec l'ID de l'entretien
        return redirect(url_for('main.page_evaluation', entretien_id=nouvel_entretien.id))
    
    return redirect(url_for('main.home'))

# --- ROUTE VERS PARAMETRAGE D'ENTRETIEN ---
@bp.route('/entretien/<int:entretien_id>')
def page_evaluation(entretien_id):
    entretien = db.session.get(Entretien, entretien_id)
    if not entretien:
        abort(404)
    user_name = current_user.username
    
    # Dictionnaire de traduction des mois
    mois_fr = {
        1: "janvier", 2: "février", 3: "mars", 4: "avril",
        5: "mai", 6: "juin", 7: "juillet", 8: "août",
        9: "septembre", 10: "octobre", 11: "novembre", 12: "décembre"
    }

    date_affichee = entretien.date_entretien # Valeur par défaut au cas où
    
    try:
        # On convertit la string "2026-01-31" en objet date
        date_obj = datetime.strptime(entretien.date_entretien, '%Y-%m-%d')
        
        # On construit la chaîne manuellement : "31" + " " + "janvier" + " " + "2026"
        nom_mois = mois_fr[date_obj.month]
        date_affichee = f"{date_obj.day} {nom_mois} {date_obj.year}"
        
    except ValueError:
        # Si le format en base n'est pas bon, on garde l'original
        pass

    return render_template('creation_entretien.html', 
                           entretien=entretien, 
                           user=user_name, 
                           date_formatted=date_affichee)

# --- ROUTE POUR SUPPRIMER L'ENTRETIEN ---
@bp.route('/delete_interview/<int:entretien_id>', methods=['POST'])
@login_required
def delete_interview(entretien_id):
    entretien = db.session.get(Entretien, entretien_id)
    if entretien is None:
        flash("Entretien non trouvé", "error")
        return redirect(url_for('main.home'))  # ajuste selon ta route home

    try:
        # Supprimer toutes les évaluations liées à cet entretien
        stmt = delete(Evaluation).where(Evaluation.entretien_id == entretien_id)
        db.session.execute(stmt)

        # Supprimer l'entretien
        db.session.delete(entretien)
        db.session.commit()
        flash("Entretien supprimé", "success")
    except Exception as e:
        db.session.rollback()
        flash("Échec suppression", "error")
    return redirect(url_for('main.home'))

# --- SAUVEGARDE LES PARAMETRES D'ENTRETIEN ---
@bp.route('/entretien/<int:entretien_id>/start_vote', methods=['POST'])
@login_required
def start_vote(entretien_id):
    """
    Crée les évaluations avec les paliers définis
    """
    entretien = db.session.get(Entretien, entretien_id)
    if not entretien:
        abort(404)

    # ✅ Supprime les évaluations existantes si elles existent
    Evaluation.query.filter_by(entretien_id=entretien.id).delete()
    db.session.commit()
    
    # ✅ Récupère les paliers du formulaire
    for skill in entretien.poste.competences:
        palier_str = request.form.get(f'palier_{skill.id}', '')
        ponderation_str = request.form.get(f'ponderation_{skill.id}', '1')
        
        try:
            palier = int(palier_str) if palier_str else 7
            ponderation = int(ponderation_str) if ponderation_str else 1
        except ValueError:
            palier = 7
            ponderation = 1
        
        # ✅ Crée l'évaluation avec le palier
        evaluation = Evaluation(
            entretien_id=entretien.id,
            competence_id=skill.id,
            palier=palier,
            ponderation=ponderation
        )
        db.session.add(evaluation)
    
    # Changer le statut de l'entretien
    entretien.statut = "Attente_RH"
    
    db.session.commit()
    
    flash(f'Évaluation lancée pour {entretien.candidat_nom}', 'success')
    return redirect(url_for('main.page_vote_rh', entretien_id=entretien.id))

# --- CREATION DE LA PAGE VOTE_RH ---
@bp.route('/vote_rh/<int:entretien_id>')
def page_vote_rh(entretien_id):
    entretien = db.session.get(Entretien, entretien_id)
    if not entretien:
        abort(404)
    user_name = current_user.username

    entretien.statut = "Attente_RH"
    db.session.commit()

    # Dictionnaire de traduction des mois
    mois_fr = {
        1: "janvier", 2: "février", 3: "mars", 4: "avril",
        5: "mai", 6: "juin", 7: "juillet", 8: "août",
        9: "septembre", 10: "octobre", 11: "novembre", 12: "décembre"
    }

    date_affichee = entretien.date_entretien # Valeur par défaut au cas où
    
    try:
        # On convertit la string "2026-01-31" en objet date
        date_obj = datetime.strptime(entretien.date_entretien, '%Y-%m-%d')

        nom_mois = mois_fr[date_obj.month]
        date_affichee = f"{date_obj.day} {nom_mois} {date_obj.year}"
        
    except ValueError:
        # Si le format en base n'est pas bon, on garde l'original
        pass

    return render_template('voteRH.html', 
                        entretien=entretien, 
                        user=user_name, 
                        date_formatted=date_affichee)

# --- SAUVEGARDE DU VOTE RH ---
@bp.route('/save_vote_rh/<int:entretien_id>', methods=['POST'])
def save_vote_rh(entretien_id):
    entretien = db.session.get(Entretien, entretien_id)
    if not entretien:
        abort(404)

    # MAJ des évaluations existantes (snapshot)
    for ev in entretien.evaluations:
        val = request.form.get(f'vote_{ev.competence_id}')
        if val:
            ev.note_rh = int(val)

    token = str(uuid.uuid4())
    entretien.token_recruteur2 = token
    entretien.statut = "Attente_Recruteur2"

    lien_guest = url_for('main.vote_guest', token=token, _external=True)

    db.session.commit()
    return redirect(url_for('main.home'))

# --- CREATION DE LA PAGE VOTE_GUEST ---
@bp.route('/vote_guest/<token>')
def vote_guest(token):
    from app.db_helpers import entretien_by_token
    
    entretien = entretien_by_token(token)
    if not entretien:
        abort(404)
    user_name = current_user.username

    if entretien.statut == "Termine":
        return "Cet entretien est déjà clôturé."
    
    existing = {e.competence_id for e in entretien.evaluations}
    for skill in entretien.poste.competences:
        if skill.id not in existing:
            db.session.add(Evaluation(entretien_id=entretien.id, competence_id=skill.id))
    db.session.commit()

    # Dictionnaire de traduction des mois
    mois_fr = {
        1: "janvier", 2: "février", 3: "mars", 4: "avril",
        5: "mai", 6: "juin", 7: "juillet", 8: "août",
        9: "septembre", 10: "octobre", 11: "novembre", 12: "décembre"
    }

    date_affichee = entretien.date_entretien
    
    try:
        # On convertit la string "2026-01-31" en objet date
        date_obj = datetime.strptime(entretien.date_entretien, '%Y-%m-%d')

        nom_mois = mois_fr[date_obj.month]
        date_affichee = f"{date_obj.day} {nom_mois} {date_obj.year}"
        
    except ValueError:
        # Si le format en base n'est pas bon, on garde l'original
        pass

    return render_template('voteGuest.html', 
                           entretien=entretien, 
                           user=user_name,
                           date_formatted=date_affichee,
                           token=token)

# --- SAUVEGARDE DU VOTE GUEST ---
@bp.route('/save_vote_guest/<token>', methods=['POST'])
def save_vote_guest(token):
    from app.db_helpers import entretien_by_token
    from app.validators import validate_note_range
    
    entretien = entretien_by_token(token)
    if not entretien:
        abort(404)
    
    # 1. Enregistrement des notes du 2ème recruteur
    for evaluation in entretien.evaluations:
        valeur_vote = request.form.get(f'vote_{evaluation.competence_id}')
        
        if valeur_vote:
            is_valid, error_msg = validate_note_range(valeur_vote)
            if not is_valid:
                return jsonify({'success': False, 'message': error_msg}), 400
            
            evaluation.note_recruteur2 = int(valeur_vote)
    
    entretien.statut = "Termine"
    entretien.token_recruteur2 = None  # <-- invalide le lien
    db.session.commit()

    return f"""
    <div style="text-align:center; margin-top:50px; font-family:sans-serif;">
        <h1>Merci, le vote est terminé !</h1>
    </div>
    """

# --- ROUTE RAPPORT ENTRETIEN ---
@bp.route('/entretien/<int:entretien_id>/rapport')
@login_required
def rapport_entretien(entretien_id):
    """Affiche le rapport d'entretien en HTML"""
    from app.db_helpers import get_entretien_by_id
    
    entretien = get_entretien_by_id(entretien_id)
    if not entretien:
        abort(404)
    
    # ✅ Calcule les stats
    stats = calculs.calculer_stat(entretien.evaluations)
    
    # ✅ Passe au template
    return render_template('rapport.html', 
                          entretien=entretien, 
                          stats=stats)

# ===== ROUTES DE TEST D'ERREURS =====
# À SUPPRIMER EN PRODUCTION !
@bp.route('/test/404')
def test_404():
    """Simule une erreur 404"""
    abort(404)

@bp.route('/test/500')
def test_500():
    """Simule une erreur 500"""
    # ✅ Utilise une erreur qui sera capturée par le gestionnaire
    try:
        raise Exception("Erreur serveur intentionnelle pour test")
    except Exception as e:
        # Flask retournera automatiquement un 500
        raise

@bp.route('/test/500/db')
def test_500_db():
    """Simule une erreur 500 avec rollback DB"""
    # Force une erreur de base de données
    db.session.rollback()
    raise Exception("Erreur serveur intentionnelle pour test")

@bp.route('/test/403')
def test_403():
    """Simule une erreur 403"""
    abort(403)

@bp.route('/test/400')
def test_400():
    """Simule une erreur 400"""
    abort(400)

@bp.route('/test/errors')
def test_errors_list():
    """Liste de tous les tests disponibles"""
    return render_template('test_errors.html')