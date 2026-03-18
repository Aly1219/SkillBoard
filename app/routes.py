from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, abort
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db
from app.models import User, Poste, Competence, Entretien, Evaluation
from datetime import datetime
from sqlalchemy import delete
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
)
from app.validators import (
    validate_note_range,
)
from app.utils import format_date_fr

# ============================================================
# TABLE DES MATIÈRES
# 1.  AUTHENTIFICATION     login / register / logout
# 2.  POSTES               get / add / update / delete
# 3.  COMPÉTENCES          add / update / delete
# 4.  ENTRETIENS           create / delete
# 5.  VOTE RH              page / sauvegarde
# 6.  VOTE GUEST           page / sauvegarde
# 7.  RAPPORT
# 8.  ROUTES DE TEST       (dev uniquement)
# ============================================================

bp = Blueprint('main', __name__)


# ============================================================
# 1. AUTHENTIFICATION
# ============================================================

@bp.route('/')
@login_required
def home():
    """Affiche le dashboard avec toutes les données"""
    data = get_dashboard_data()
    return render_template('index.html',
                           user=current_user.username,
                           jobs=data['postes'],
                           all_skills=data['all_competences'],
                           entretiens=data['entretiens'])


@bp.route('/login', methods=['GET', 'POST'])
def login():
    # Si déjà connecté, on redirige directement
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))

    # Première connexion : aucun utilisateur en base → inscription forcée
    if not user_exists():
        return redirect(url_for('main.register'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = get_user_by_username(username)

        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('main.home'))
        else:
            flash("Nom d'utilisateur ou mot de passe incorrect")

    return render_template('login.html')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    # Sécurité : un seul compte autorisé — on bloque si un utilisateur existe déjà
    if user_exists() and not current_user.is_authenticated:
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        new_user = User(username=username)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return redirect(url_for('main.home'))

    return render_template('register.html')


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))


# ============================================================
# 2. POSTES
# ============================================================

@bp.route('/api/poste/<int:poste_id>')
@login_required
def get_poste_details(poste_id):
    """Retourne les détails d'un poste en JSON (utilisé par le JS du dashboard)"""
    poste = get_poste_by_id(poste_id)
    if not poste:
        abort(404)
    skills = [{"id": c.id, "nom": c.nom} for c in poste.competences]
    return jsonify({"nom": poste.nom, "competences": skills})


@bp.route('/add_poste', methods=['POST'])
@login_required
def add_poste():
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


@bp.route('/update_poste', methods=['POST'])
@login_required
def update_poste():
    poste_id = request.form.get('poste_id')
    nom_poste = request.form.get('nom_poste')
    competences_ids = request.form.getlist('competences')

    poste = get_poste_by_id(poste_id)

    if poste:
        poste.nom = nom_poste
        poste.competences = [
            skill for skill_id in competences_ids
            if (skill := get_competence_by_id(int(skill_id)))
        ]

        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            db.session.app.logger.error(f"Erreur update_poste : {e}")

    return redirect(url_for('main.home'))


@bp.route('/api/poste/<int:poste_id>', methods=['DELETE'])
@login_required
def api_delete_poste(poste_id):
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


# ============================================================
# 3. COMPÉTENCES
# ============================================================

@bp.route('/add_competence', methods=['POST'])
@login_required
def add_competence():
    nom = request.form.get('nom_competence')

    if nom:
        # Vérification doublon avant insertion
        if not get_competence_by_name(nom):
            db.session.add(Competence(nom=nom))
            db.session.commit()

    return redirect(url_for('main.home'))


@bp.route('/api/competence/<int:competence_id>', methods=['PUT'])
@login_required
def update_competence(competence_id):
    """Renomme une compétence — vérifie que le nouveau nom n'existe pas déjà"""
    competence = get_competence_by_id(competence_id)
    if not competence:
        return jsonify({'success': False, 'message': 'Compétence non trouvée'}), 404

    data = request.get_json()
    nouveau_nom = (data.get('nom') or '').strip()

    if not nouveau_nom:
        return jsonify({'success': False, 'message': 'Le nom est requis'}), 400

    # Vérification doublon (en ignorant la compétence elle-même)
    existante = get_competence_by_name(nouveau_nom)
    if existante and existante.id != competence_id:
        return jsonify({'success': False, 'message': 'Ce nom existe déjà'}), 409

    competence.nom = nouveau_nom
    db.session.commit()
    return jsonify({'success': True, 'competence': {'id': competence.id, 'nom': competence.nom}}), 200


@bp.route('/api/competence/<int:competence_id>', methods=['DELETE'])
@login_required
def delete_competence(competence_id):
    """
    Supprime une compétence uniquement si elle n'est liée à aucun poste
    ni à aucune évaluation en cours.
    """
    competence = get_competence_by_id(competence_id)
    if not competence:
        return jsonify({'success': False, 'message': 'Compétence non trouvée'}), 404

    # Vérification : liée à au moins un poste ?
    if competence.postes:
        noms_postes = ', '.join(p.nom for p in competence.postes)
        return jsonify({
            'success': False,
            'message': f'Impossible de supprimer : cette compétence est liée au(x) poste(s) "{noms_postes}".'
        }), 409

    # Vérification : utilisée dans une évaluation ?
    evaluations = Evaluation.query.filter_by(competence_id=competence_id).first()
    if evaluations:
        return jsonify({
            'success': False,
            'message': 'Impossible de supprimer : cette compétence est utilisée dans un ou plusieurs entretiens.'
        }), 409

    db.session.delete(competence)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Compétence supprimée'}), 200


# ============================================================
# 4. ENTRETIENS
# ============================================================

@bp.route('/create_interview', methods=['POST'])
@login_required
def create_interview():
    from datetime import date as date_type

    nom = request.form.get('cand_nom')
    prenom = request.form.get('cand_prenom')
    date_str = request.form.get('entr_date')
    recruteur2 = request.form.get('entr_recruteur')
    poste_nom = request.form.get('entr_poste')

    # Conversion de la chaîne ISO reçue du formulaire en objet date Python
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        flash("Format de date invalide", "error")
        return redirect(url_for('main.home'))

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

        # SNAPSHOT : on lie les compétences du poste à cet entretien au moment
        # de sa création. Si le poste évolue demain, cet entretien n'est pas impacté.
        for competence in poste.competences:
            db.session.add(Evaluation(
                entretien_id=nouvel_entretien.id,
                competence_id=competence.id,
            ))
        db.session.commit()

        return redirect(url_for('main.page_evaluation', entretien_id=nouvel_entretien.id))

    return redirect(url_for('main.home'))


@bp.route('/delete_interview/<int:entretien_id>', methods=['POST'])
@login_required
def delete_interview(entretien_id):
    entretien = db.session.get(Entretien, entretien_id)
    if entretien is None:
        flash("Entretien non trouvé", "error")
        return redirect(url_for('main.home'))

    try:
        db.session.execute(delete(Evaluation).where(Evaluation.entretien_id == entretien_id))
        db.session.delete(entretien)
        db.session.commit()
        flash("Entretien supprimé", "success")
    except Exception:
        db.session.rollback()
        flash("Échec de la suppression", "error")

    return redirect(url_for('main.home'))


@bp.route('/entretien/<int:entretien_id>')
@login_required
def page_evaluation(entretien_id):
    entretien = db.session.get(Entretien, entretien_id)
    if not entretien:
        abort(404)

    return render_template('creation_entretien.html',
                           entretien=entretien,
                           user=current_user.username,
                           date_formatted=format_date_fr(entretien.date_entretien))


# ============================================================
# 5. VOTE RH
# ============================================================

@bp.route('/entretien/<int:entretien_id>/start_vote', methods=['POST'])
@login_required
def start_vote(entretien_id):
    """Enregistre les paliers et lance la phase de vote RH"""
    entretien = db.session.get(Entretien, entretien_id)
    if not entretien:
        abort(404)

    # On recrée les évaluations avec les paliers saisis dans le formulaire
    Evaluation.query.filter_by(entretien_id=entretien.id).delete()
    db.session.commit()

    for skill in entretien.poste.competences:
        palier_str = request.form.get(f'palier_{skill.id}', '')
        ponderation_str = request.form.get(f'ponderation_{skill.id}', '1')

        try:
            palier = int(palier_str) if palier_str else calculs.PALIER_DEFAUT
            ponderation = int(ponderation_str) if ponderation_str else 1
        except ValueError:
            palier = calculs.PALIER_DEFAUT
            ponderation = 1

        db.session.add(Evaluation(
            entretien_id=entretien.id,
            competence_id=skill.id,
            palier=palier,
            ponderation=ponderation
        ))

    entretien.statut = "Attente_RH"
    db.session.commit()

    flash(f'Évaluation lancée pour {entretien.candidat_nom}', 'success')
    return redirect(url_for('main.page_vote_rh', entretien_id=entretien.id))


@bp.route('/vote_rh/<int:entretien_id>')
@login_required
def page_vote_rh(entretien_id):
    entretien = db.session.get(Entretien, entretien_id)
    if not entretien:
        abort(404)

    entretien.statut = "Attente_RH"
    db.session.commit()

    return render_template('voteRH.html',
                           entretien=entretien,
                           user=current_user.username,
                           date_formatted=format_date_fr(entretien.date_entretien))


@bp.route('/save_vote_rh/<int:entretien_id>', methods=['POST'])
@login_required
def save_vote_rh(entretien_id):
    entretien = db.session.get(Entretien, entretien_id)
    if not entretien:
        abort(404)

    for ev in entretien.evaluations:
        val = request.form.get(f'vote_{ev.competence_id}')
        if val:
            ev.note_rh = int(val)

    token = str(uuid.uuid4())
    entretien.token_recruteur2 = token
    entretien.statut = "Attente_Recruteur2"
    db.session.commit()

    return redirect(url_for('main.home'))


# ============================================================
# 6. VOTE GUEST (recruteur externe — accès par token)
# ============================================================

@bp.route('/vote_guest/<token>')
def vote_guest(token):
    entretien = entretien_by_token(token)
    if not entretien:
        abort(404)

    if entretien.statut == "Termine":
        return render_template('vote_cloture.html')

    # Sécurité : on ne récupère le username que si l'utilisateur est authentifié
    user_name = current_user.username if current_user.is_authenticated else "Recruteur externe"

    # On s'assure que toutes les compétences ont bien une évaluation liée
    existing = {e.competence_id for e in entretien.evaluations}
    for skill in entretien.poste.competences:
        if skill.id not in existing:
            db.session.add(Evaluation(entretien_id=entretien.id, competence_id=skill.id))
    db.session.commit()

    return render_template('voteGuest.html',
                           entretien=entretien,
                           user=user_name,
                           date_formatted=format_date_fr(entretien.date_entretien),
                           token=token)


@bp.route('/save_vote_guest/<token>', methods=['POST'])
def save_vote_guest(token):
    entretien = entretien_by_token(token)
    if not entretien:
        abort(404)

    for evaluation in entretien.evaluations:
        valeur_vote = request.form.get(f'vote_{evaluation.competence_id}')

        if valeur_vote:
            is_valid, error_msg = validate_note_range(valeur_vote)
            if not is_valid:
                return jsonify({'success': False, 'message': error_msg}), 400
            evaluation.note_recruteur2 = int(valeur_vote)

    entretien.statut = "Termine"
    entretien.token_recruteur2 = None  # Invalide le lien après usage
    db.session.commit()

    return render_template('vote_merci.html')


# ============================================================
# 7. RAPPORT
# ============================================================

@bp.route('/entretien/<int:entretien_id>/rapport')
@login_required
def rapport_entretien(entretien_id):
    """Affiche le rapport d'entretien en HTML"""
    entretien = get_entretien_by_id(entretien_id)
    if not entretien:
        abort(404)

    stats = calculs.calculer_stat(entretien.evaluations)
    return render_template('rapport.html', entretien=entretien, stats=stats)


# ============================================================
# 8. ROUTES DE TEST (dev uniquement — retirées en production)
# ============================================================

@bp.route('/test/404')
def test_404():
    abort(404)

@bp.route('/test/500')
def test_500():
    raise Exception("Erreur 500 intentionnelle")

@bp.route('/test/500/db')
def test_500_db():
    db.session.rollback()
    raise Exception("Erreur 500 DB intentionnelle")

@bp.route('/test/403')
def test_403():
    abort(403)

@bp.route('/test/400')
def test_400():
    abort(400)

@bp.route('/test/errors')
def test_errors_list():
    return render_template('test_errors.html')