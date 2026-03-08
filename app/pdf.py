import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd
import unicodedata
import tempfile
import os
from fpdf import FPDF

sns.set_style("whitegrid")

# ============================================================
# UTILITAIRES
# ============================================================

def _nettoyer_texte(texte):
    """Enlève les accents pour compatibilité latin-1"""
    if not isinstance(texte, str):
        return texte
    nfd = unicodedata.normalize('NFD', texte)
    return ''.join(c for c in nfd if unicodedata.category(c) != 'Mn')


def _figure_to_image(fig):
    """Convertit une figure matplotlib en fichier PNG temporaire"""
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        fig.savefig(tmp.name, format='png', dpi=100, bbox_inches='tight')
        plt.close(fig)
        return tmp.name

# ============================================================
# SECTION 1 : GRAPHIQUES
# ============================================================
# Cette section crée les 3 graphiques
# À MODIFIER : Ici pour changer l'apparence des graphiques

def _create_radar_chart(stats):
    """Graphique en toile d'araignée avec paliers personnalisés"""
    df = pd.DataFrame(stats['details'])
    
    competences = df['competence'].tolist()
    moyennes = df['moyenne'].tolist()
    paliers = df['palier'].tolist()
    
    num_vars = len(competences)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    
    moyennes += moyennes[:1]
    paliers += paliers[:1]
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(projection='polar'))
    
    ax.plot(angles, paliers, 'r-', linewidth=2, label='Palier requis')
    ax.fill(angles, paliers, alpha=0.15, color='red')
    
    ax.plot(angles, moyennes, 'b-', linewidth=2, label='Performance')
    ax.fill(angles, moyennes, alpha=0.25, color='blue')
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(competences, size=8)
    ax.set_ylim(0, 10)
    ax.set_yticks([2, 4, 6, 8, 10])
    ax.set_rlabel_position(0)
    
    plt.title('Toile d\'Araignee - Performance vs Palier', fontsize=10, fontweight='bold', pad=15)
    plt.legend(loc='upper right', bbox_to_anchor=(1.2, 1.0), fontsize=8)
    plt.tight_layout()
    
    return fig


def _create_pyramid_chart(stats):
    """Graphique en pyramide avec paliers personnalisés"""
    df = pd.DataFrame(stats['details_tries'])
    
    fig, ax = plt.subplots(figsize=(8, 5))
    
    colors = ['#2ecc71' if row['moyenne'] >= row['palier'] else '#e74c3c' 
              for idx, row in df.iterrows()]
    
    ax.barh(range(len(df)), df['moyenne'], color=colors, alpha=0.8, label='Performance')
    ax.set_yticks(range(len(df)))
    ax.set_yticklabels(df['competence'], fontsize=9)
    ax.set_xlabel('Note (/10)', fontsize=10)
    ax.set_xlim(0, 10)
    ax.invert_yaxis()
    
    for i, (idx, row) in enumerate(df.iterrows()):
        ax.plot([row['palier'], row['palier']], [i - 0.4, i + 0.4], 
                color='red', linewidth=2, linestyle='--')
    
    for i, v in enumerate(df['moyenne']):
        ax.text(v + 0.2, i, f'{v:.1f}', va='center', fontsize=8, fontweight='bold')
    
    plt.title('Classement des Competences (Meilleures au Pires)', fontsize=10, fontweight='bold')
    plt.tight_layout()
    
    return fig


def _create_delta_palier_chart(stats):
    """Graphique en barre avec écart personnalisé par compétence"""
    df = pd.DataFrame(stats['details_tries'])
    
    df['delta'] = df['moyenne'] - df['palier']
    
    fig, ax = plt.subplots(figsize=(8, 5))
    
    colors = ['#2ecc71' if x >= 0 else '#e74c3c' for x in df['delta']]
    ax.bar(range(len(df)), df['delta'], color=colors, alpha=0.8)
    
    ax.axhline(y=0, color='black', linestyle='-', linewidth=2)
    
    ax.set_xticks(range(len(df)))
    ax.set_xticklabels(df['competence'], rotation=45, ha='right', fontsize=9)
    ax.set_ylabel('Ecart par rapport au palier', fontsize=10)
    ax.set_xlabel('Competences', fontsize=10)
    ax.set_title('Ecart a Atteindre (Negatif = Sous-performant)', fontsize=10, fontweight='bold')
    
    for i, v in enumerate(df['delta']):
        ax.text(i, v + 0.1 if v >= 0 else v - 0.3, f'{v:.1f}', 
                ha='center', fontsize=8, fontweight='bold')
    
    plt.tight_layout()
    
    return fig

# ============================================================
# SECTION 2 : CONTENU DE LA PAGE 1
# ============================================================
# Cette section crée le contenu de la première page (titre, infos, tableau)
# À MODIFIER : Ici pour ajouter/retirer des colonnes au tableau

def _ajouter_en_tete(pdf, entretien, stats, font_name):
    """
    Ajoute le titre et les infos du candidat en haut de la page
    
    À MODIFIER :
    - Changer les couleurs (bg-primary, etc.)
    - Modifier le texte des labels
    - Ajouter/retirer des champs
    """
    # Titre
    pdf.set_font(font_name, 'B', 16)
    pdf.cell(0, 10, 
             txt=f"Rapport d'Entretien : {_nettoyer_texte(entretien.candidat_nom)} {_nettoyer_texte(entretien.candidat_prenom)}", 
             ln=1,
             align='C')
    pdf.ln(10)

    # Infos candidat
    pdf.set_font(font_name, size=11)
    pdf.cell(0, 10, txt=f"Candidat : {_nettoyer_texte(entretien.candidat_nom)} {_nettoyer_texte(entretien.candidat_prenom)}", ln=1)
    pdf.cell(0, 10, txt=f"Poste : {_nettoyer_texte(entretien.poste.nom)}", ln=1)
    pdf.cell(0, 10, txt=f"Recruteurs : {_nettoyer_texte(entretien.recruteur_secondaire)} (et RH)", ln=1)
    pdf.cell(0, 10, txt=f"Date : {entretien.date_entretien}", ln=1)
    pdf.ln(10)

    # Score global
    pdf.set_font(font_name, 'B', 12)
    score_global = stats.get('score_global', 0)
    pdf.cell(0, 10, txt=f"Score Global : {score_global}/10", ln=1)
    pdf.ln(5)


def _ajouter_tableau_evals(pdf, stats, font_name):
    """
    Ajoute le tableau récapitulatif des évaluations
    
    À MODIFIER :
    - Ajouter/retirer des colonnes en changeant les cell()
    - Changer la largeur des colonnes (1er paramètre des cell)
    - Changer le nom des colonnes (txt=)
    
    EXEMPLE : Si tu veux ajouter la colonne "Palier":
    pdf.cell(20, 7, txt="Palier", border=1, align='C')
    Et dans la boucle:
    pdf.cell(20, 7, txt=f"{detail.get('palier', '-')}/10", border=1, align='C')
    """
    
    # EN-TÊTE DU TABLEAU
    pdf.set_font(font_name, 'B', 10)
    
    # ✅ MODIFIE ICI pour ajouter des colonnes
    pdf.cell(50, 7, txt="Competence", border=1)          # Largeur 50
    pdf.cell(20, 7, txt="RH", border=1, align='C')        # Largeur 20
    pdf.cell(20, 7, txt="Rec. 2", border=1, align='C')    # Largeur 20
    pdf.cell(25, 7, txt="Moyenne", border=1, align='C')   # Largeur 25
    pdf.cell(20, 7, txt="Palier", border=1, align='C')    # ✅ NOUVELLE COLONNE - Largeur 20
    pdf.cell(20, 7, txt="Ecart", border=1, align='C')     # Largeur 20
    pdf.cell(20, 7, txt="Statut", border=1, align='C')    # Largeur 20
    pdf.ln(7)

    # CONTENU DU TABLEAU
    pdf.set_font(font_name, size=9)
    for detail in stats.get('details', []):
        competence = _nettoyer_texte(str(detail.get('competence', '')))
        note_rh = int(detail.get('note_rh', 0))
        note_rec2 = int(detail.get('note_rec2', 0))
        moyenne = float(detail.get('moyenne', 0))
        ecart = float(detail.get('ecart', 0))
        palier = int(detail.get('palier', 7))                    # ✅ RÉCUPÈRE LE PALIER
        atteint = "OUI" if detail.get('atteint_palier', False) else "NON"  # ✅ CALCULE LE STATUT

        # ✅ MODIFIE ICI pour ajouter des colonnes
        pdf.cell(50, 7, txt=competence[:30], border=1)
        pdf.cell(20, 7, txt=f"{note_rh}", border=1, align='C')
        pdf.cell(20, 7, txt=f"{note_rec2}", border=1, align='C')
        pdf.cell(25, 7, txt=f"{moyenne:.1f}", border=1, align='C')
        pdf.cell(20, 7, txt=f"{palier}", border=1, align='C')   # ✅ AFFICHE LE PALIER
        pdf.cell(20, 7, txt=f"{ecart:.1f}", border=1, align='C')
        pdf.cell(20, 7, txt=atteint, border=1, align='C')       # ✅ AFFICHE LE STATUT
        pdf.ln(7)

    pdf.ln(10)


def _ajouter_analyses(pdf, stats, font_name):
    """
    Ajoute la section "Analyses" avec les infos clés
    
    À MODIFIER :
    - Changer le texte des analyses
    - Ajouter/retirer des analyses
    """
    pdf.set_font(font_name, 'B', 11)
    pdf.cell(0, 8, txt="Analyses", ln=1)
    pdf.ln(3)

    pdf.set_font(font_name, size=10)
    
    meilleure = stats.get('meilleure_competence', 'N/A')
    meilleure_note = stats.get('meilleure_note', 0)
    pdf.cell(0, 6, txt=f"* Meilleure competence : {_nettoyer_texte(meilleure)} ({meilleure_note}/10)", ln=1)
    
    pire = stats.get('pire_competence', 'N/A')
    pire_note = stats.get('pire_note', 0)
    pdf.cell(0, 6, txt=f"* Moins bonne competence : {_nettoyer_texte(pire)} ({pire_note}/10)", ln=1)
    
    sous_palier = stats.get('competences_sous_palier', [])
    if sous_palier:
        pdf.cell(0, 6, txt=f"* Competences sous le palier :", ln=1)
        for comp in sous_palier:
            nom = _nettoyer_texte(comp['competence'])
            moyenne = comp['moyenne']
            palier = comp['palier']
            manquant = palier - moyenne
            pdf.cell(10, 6, txt="")
            pdf.cell(0, 6, txt=f"  - {nom} : {moyenne:.1f} (palier {palier}/10, manque {manquant:.1f})", ln=1)
    else:
        pdf.cell(0, 6, txt=f"* Toutes les competences atteignent leur palier respectif !", ln=1)
    
    pdf.ln(5)


def _ajouter_alertes(pdf, stats, font_name):
    """
    Ajoute la section "Alertes" pour les divergences
    
    À MODIFIER :
    - Changer le seuil d'alerte (actuellement ecart > 2)
    - Changer le texte des alertes
    """
    pdf.set_font(font_name, 'B', 11)
    pdf.cell(0, 8, txt="Alertes - Divergences entre evaluateurs", ln=1)
    
    pdf.set_font(font_name, size=10)
    alertes = [d for d in stats.get('details', []) if d['alerte']]
    
    if alertes:
        for detail in alertes:
            competence = _nettoyer_texte(detail['competence'])
            note_rh = detail['note_rh']
            note_rec2 = detail['note_rec2']
            ecart = detail['ecart']
            pdf.cell(0, 6, txt=f"* {competence} : RH={note_rh}, Rec2={note_rec2} (ecart de {ecart})", ln=1)
    else:
        pdf.set_font(font_name, 'I', 10)
        pdf.cell(0, 6, txt="Aucun ecart significatif detecte", ln=1)

# ============================================================
# SECTION 3 : RECOMMANDATIONS
# ============================================================
# À MODIFIER : Ici pour changer les recommandations

def _generer_recommandations(stats):
    """Génère les recommandations basées sur les stats"""
    recommendations = []
    
    meilleure = stats['meilleure_competence']
    recommendations.append({
        'titre': f'1. Force identifiee : {_nettoyer_texte(meilleure)}',
        'texte': f'Le candidat a demontre une excellente performance en {_nettoyer_texte(meilleure)} avec une note de {stats["meilleure_note"]}/10. Cette force pourrait etre exploitee au sein de l\'equipe.'
    })
    
    pire = stats['pire_competence']
    recommendations.append({
        'titre': f'2. Point d\'amelioration : {_nettoyer_texte(pire)}',
        'texte': f'La competence {_nettoyer_texte(pire)} necessite une amelioration avec une note actuelle de {stats["pire_note"]}/10. Une formation ou du mentorat pourrait etre envisage.'
    })
    
    if stats['competences_sous_palier']:
        num_sous = stats['nombre_sous_palier']
        total = len(stats['details'])
        pourcentage = stats['pourcentage_sous_palier']
        recommendations.append({
            'titre': f'3. Competences sous le palier ({num_sous}/{total})',
            'texte': f'{pourcentage}% des competences evaluees ne respectent pas leur palier minimum. Une attention particuliere devrait etre portee a ces elements avant l\'embauche.'
        })
    else:
        recommendations.append({
            'titre': '3. Candidat performant',
            'texte': f'Excellent ! Le candidat respecte le palier pour toutes les competences evaluees.'
        })
    
    ecarts = [d['ecart'] for d in stats['details']]
    ecart_moyen = sum(ecarts) / len(ecarts) if ecarts else 0
    
    if ecart_moyen < 1:
        recommendations.append({
            'titre': '4. Consensus entre evaluateurs',
            'texte': f'Excellent consensus entre les evaluateurs (ecart moyen de {ecart_moyen:.1f}). Les evaluations sont coherentes et fiables.'
        })
    else:
        recommendations.append({
            'titre': '4. Divergences d\'evaluation',
            'texte': f'L\'ecart moyen entre les evaluateurs est de {ecart_moyen:.1f}. Une discussion est recommandee pour clarifier les divergences d\'opinion.'
        })
    
    return recommendations

# ============================================================
# SECTION 4 : FONCTION PRINCIPALE
# ============================================================
# C'est ici que tout s'assemble

def generer_rapport(entretien, stats) -> bytes:
    """
    Génère le rapport PDF complet
    
    Structure :
    - Page 1 : Infos, tableau, analyses, alertes
    - Page 2 : Graphique radar
    - Page 3 : Graphique pyramide
    - Page 4 : Graphique delta
    - Page 5 : Recommandations
    """
    
    pdf = FPDF()
    pdf.compress = False
    
    # Configuration de la police
    try:
        pdf.add_font("DejaVu", "", "/Library/Fonts/DejaVuSans.ttf")
        pdf.add_font("DejaVu", "B", "/Library/Fonts/DejaVuSans-Bold.ttf")
        pdf.add_font("DejaVu", "I", "/Library/Fonts/DejaVuSans-Oblique.ttf")
        font_name = "DejaVu"
    except:
        font_name = "Arial"
    
    # ============================================================
    # PAGE 1 : INFOS ET TABLEAU
    # ============================================================
    pdf.add_page()
    
    _ajouter_en_tete(pdf, entretien, stats, font_name)
    _ajouter_tableau_evals(pdf, stats, font_name)
    _ajouter_analyses(pdf, stats, font_name)
    _ajouter_alertes(pdf, stats, font_name)

    # ============================================================
    # PAGE 2 : GRAPHIQUE RADAR
    # ============================================================
    try:
        pdf.add_page()
        fig_radar = _create_radar_chart(stats)
        img_path = _figure_to_image(fig_radar)
        pdf.image(img_path, x=10, y=30, w=190)
        os.remove(img_path)
    except Exception as e:
        pdf.set_font(font_name, 'I', 9)
        pdf.cell(0, 5, txt=f"Erreur generation radar: {str(e)}", ln=1)

    # ============================================================
    # PAGE 3 : GRAPHIQUE PYRAMIDE
    # ============================================================
    try:
        pdf.add_page()
        fig_pyramid = _create_pyramid_chart(stats)
        img_path = _figure_to_image(fig_pyramid)
        pdf.image(img_path, x=10, y=30, w=190)
        os.remove(img_path)
    except Exception as e:
        pdf.set_font(font_name, 'I', 9)
        pdf.cell(0, 5, txt=f"Erreur generation pyramide: {str(e)}", ln=1)

    # ============================================================
    # PAGE 4 : GRAPHIQUE DELTA PALIER
    # ============================================================
    try:
        pdf.add_page()
        fig_delta = _create_delta_palier_chart(stats)
        img_path = _figure_to_image(fig_delta)
        pdf.image(img_path, x=10, y=30, w=190)
        os.remove(img_path)
    except Exception as e:
        pdf.set_font(font_name, 'I', 9)
        pdf.cell(0, 5, txt=f"Erreur generation delta: {str(e)}", ln=1)

    # ============================================================
    # PAGE 5 : RECOMMANDATIONS
    # ============================================================
    pdf.add_page()
    pdf.set_font(font_name, 'B', 14)
    pdf.cell(0, 10, txt="Recommandations", ln=1, align='C')
    pdf.ln(5)

    pdf.set_font(font_name, size=10)
    
    recommandations = _generer_recommandations(stats)
    for rec in recommandations:
        pdf.set_font(font_name, 'B', 10)
        pdf.cell(0, 6, txt=rec['titre'], ln=1)
        pdf.set_font(font_name, size=9)
        pdf.cell(5, 5, txt="")
        pdf.multi_cell(0, 5, txt=rec['texte'])
        pdf.ln(3)

    # ============================================================
    # RETOUR PDF
    # ============================================================
    pdf_output = pdf.output(dest='S')
    
    if isinstance(pdf_output, str):
        return pdf_output.encode('latin-1')
    
    return pdf_output