from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash, send_file, abort
from flask_login import login_user, logout_user, login_required, current_user
from app.extensions import db, cache
from app.models import User, Poste, Competence, Entretien, Evaluation
from datetime import datetime
import uuid
import app.calculs as calculs
import app.pdf as pdf
import io # permet de gérer des flux d'E/S, pour écrire avec des données en byte(str). 

# On définit un blueprint nommé 'main'
bp = Blueprint('main', __name__)

# --- ROUTE D'ACCUEIL (DASHBOARD) ---
@bp.route('/')
@login_required
def home():
    # 1. On récupère les données depuis la base de données
    postes = Poste.query.order_by(Poste.nom.asc()).all()
    all_competences = Competence.query.order_by(Competence.nom.asc()).all()
    entretiens = Entretien.query.order_by(Entretien.date_entretien.asc()).all()

    # 2. On les envoie au template
    return render_template('index.html', 
                           user=current_user.username,
                           jobs=postes,
                           all_skills=all_competences,
                           entretiens=entretiens)

# --- ROUTE LOGIN ---
@bp.route('/login', methods=['GET', 'POST'])
def login():
    # Si l'utilisateur est déjà connecté, on l'envoie au dashboard
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    # LOGIQUE (1) - Première connexion
    # Si aucun utilisateur n'existe dans la base, on force la redirection vers l'inscription
    if not User.query.first():
        return redirect(url_for('main.register'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()

        #Vérification du mot de passe
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('main.home'))
        else:
            flash('Nom d\'utilisateur ou mot de passe incorrect')
    return render_template('login.html')

# --- ROUTE INSCRIPTION ---
@bp.route('/register', methods=['GET', 'POST'])
def register():
    # Sécurité : Si un utilisateur existe déjà, on empêche d'en créer un nouveau
    if User.query.first() and not current_user.is_authenticated:
        return redirect(url_for('main.login'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Création du nouvel utilisateur
        new_user = User(username=username)
        new_user.set_password(password) # Hachage du mot de passe
        
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
    poste = Poste.query.get_or_404(poste_id)
    skills = [{"id": c.id, "nom": c.nom} for c in poste.competences]
    return jsonify({
        "nom": poste.nom,
        "competences": skills
    })

# --- ROUTE AJOUTER POSTE ---
@bp.route('/add_poste', methods=['POST'])
def add_poste():
    nom = request.form.get('nom_poste')
    skill_ids = request.form.getlist('competences')
    
    if nom:
        nouveau_poste = Poste(nom=nom)
        for s_id in skill_ids:
            comp = Competence.query.get(s_id)
            if comp:
                nouveau_poste.competences.append(comp)
        
        db.session.add(nouveau_poste)
        db.session.commit()
        
    return redirect(url_for('main.home'))

# --- ROUTE MODIFIER UN POSTE ---
@bp.route('/update_poste', methods=['POST'])
def update_poste():
    # 1. Récupération des données du formulaire
    poste_id = request.form.get('poste_id')
    nom_poste = request.form.get('nom_poste')
    competences_ids = request.form.getlist('competences') 

    # 2. Recherche du poste dans la base de données
    poste = Poste.query.get(poste_id)

    if poste:
        # 3. Mise à jour du nom
        poste.nom = nom_poste

        # 4. Mise à jour des compétences
        nouvelle_liste_competences = []
        for skill_id in competences_ids:
            skill = Competence.query.get(int(skill_id))
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
    poste = Poste.query.get(poste_id)
    if not poste:
        return jsonify({'success': False, 'message': 'Poste non trouvé'}), 404

    try:
        db.session.delete(poste)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Poste supprimé', 'poste': {'id': poste.id, 'nom': poste.nom}}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Erreur serveur'}), 500

# --- ROUTE AJOUTER COMPETENCE ---
@bp.route('/add_competence', methods=['POST'])
@login_required
def add_competence():
    nom = request.form.get('nom_competence')
    
    if nom:
        # On vérifie si la compétence existe déjà pour éviter les doublons
        existe = Competence.query.filter_by(nom=nom).first()
        
        if not existe:
            nouvelle_comp = Competence(nom=nom)
            db.session.add(nouvelle_comp)
            db.session.commit()
            
    return redirect(url_for('main.home'))

# --- ROUTE TRAITEMENT DU FORMULAIRE DE CREATION D'ENTRETIEN ---
@bp.route('/create_interview', methods=['POST'])
def create_interview():
    # Récupération des données du formulaire
    nom = request.form.get('cand_nom')
    prenom = request.form.get('cand_prenom')
    date = request.form.get('entr_date')
    recruteur2 = request.form.get('entr_recruteur')
    poste_nom = request.form.get('entr_poste')
    
    # Trouver le poste correspondant (pour lier les compétences)
    poste = Poste.query.filter_by(nom=poste_nom).first()
    
    if poste:
        nouvel_entretien = Entretien(
            candidat_nom=nom,
            candidat_prenom=prenom,
            date_entretien=date,
            recruteur_secondaire=recruteur2,
            poste=poste
        )
        db.session.add(nouvel_entretien)
        db.session.flush() # Pour générer l'ID de l'entretien tout de suite
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
    entretien = Entretien.query.get_or_404(entretien_id)
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
    entretien = Entretien.query.get(entretien_id)
    if entretien is None:
        flash("Entretien non trouvé", "error")
        return redirect(url_for('main.home'))  # ajuste selon ta route home

    try:
        # Suppression des évaluations liées
        Evaluation.query.filter_by(entretien_id=entretien_id).delete()
        db.session.delete(entretien)
        db.session.commit()
        flash("Entretien supprimé", "success")
    except Exception as e:
        db.session.rollback()
        flash("Échec suppression", "error")
    return redirect(url_for('main.home'))

# --- SAUVEGARDE LES PARAMETRES D'ENTRETIEN ---
@bp.route('/start_vote/<int:entretien_id>', methods=['POST'])
def start_vote(entretien_id):
    entretien = Entretien.query.get_or_404(entretien_id)

    # 1) Figer les compétences (snapshot) -> créer les Evaluation manquantes
    existing = {e.competence_id for e in entretien.evaluations}
    for skill in entretien.poste.competences:
        if skill.id not in existing:
            db.session.add(Evaluation(
                entretien_id=entretien.id,
                competence_id=skill.id
            ))

    # 2) Changer le statut
    entretien.statut = "Attente_RH"

    db.session.commit()

    return redirect(url_for('main.page_vote_rh', entretien_id=entretien.id))

# --- CREATION DE LA PAGE VOTE_RH ---
@bp.route('/vote_rh/<int:entretien_id>')
def page_vote_rh(entretien_id):
    entretien = Entretien.query.get_or_404(entretien_id)
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
    entretien = Entretien.query.get_or_404(entretien_id)

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
    entretien = Entretien.query.filter_by(token_recruteur2=token).first_or_404()
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

    date_affichee = entretien.date_entretien # Valeur par défaut au cas où
    
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
    entretien = Entretien.query.filter_by(token_recruteur2=token).first_or_404()
    
    # 1. Enregistrement des notes du 2ème recruteur
    for evaluation in entretien.evaluations:
        valeur_vote = request.form.get(f'vote_{evaluation.competence_id}')
        
        if valeur_vote:
            evaluation.note_recruteur2 = int(valeur_vote)
    
    entretien.statut = "Termine"
    entretien.token_recruteur2 = None  # <-- invalide le lien
    db.session.commit()

    return f"""
    <div style="text-align:center; margin-top:50px; font-family:sans-serif;">
        <h1>Merci, le vote est terminé !</h1>
    </div>
    """
    
# --- CALCULS STATS + PDF EN CACHE ---
@bp.route('/entretien/<int:entretien_id>/pdf')
@login_required
def entretien_pdf(entretien_id):
    key = f"pdf:{entretien_id}"
    pdf_bytes = cache.get(key)

    if pdf_bytes is None:
        entretien = Entretien.query.get_or_404(entretien_id)
        stats = calculs.calculer_stat(entretien)
        pdf_bytes = pdf.generer_rapport(entretien, stats)
        cache.set(key, pdf_bytes, timeout=3600)  # 1h

    return send_file(io.BytesIO(pdf_bytes),
                     mimetype="application/pdf",
                     as_attachment=True,
                     download_name=f"rapport_{entretien_id}.pdf")