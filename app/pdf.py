from fpdf import FPDF
import io

def generer_rapport(entretien, stats) -> bytes:
    """
    Génère un rapport PDF avec les résultats d'évaluation d'un entretien.
    """
    
    # ===========================================================
    # INITIALISATION DU PDF
    # ===========================================================
    pdf = FPDF()
    pdf.add_page()

    # ===========================================================
    # 1. TITRE PRINCIPAL
    # ===========================================================
    pdf.set_font("Arial", 'B', 16)  # Police Arial, Bold, taille 16
    pdf.cell(0, 10, 
             txt=f"Rapport d'Entretien : {entretien.candidat_nom} {entretien.candidat_prenom}", 
             ln=1,  # ln=1 : passe à la ligne après
             align='C')  # Centré
    pdf.ln(10)  # Saute 10 pixels

    # ===========================================================
    # 2. INFORMATIONS DU CANDIDAT
    # ===========================================================
    pdf.set_font("Arial", size=11)  # Police normale, taille 11
    
    # Ligne 1 : Nom et prénom
    pdf.cell(0, 10, 
             txt=f"Candidat : {entretien.candidat_nom} {entretien.candidat_prenom}", 
             ln=1)
    
    # Ligne 2 : Poste
    pdf.cell(0, 10, 
             txt=f"Poste : {entretien.poste.nom}", 
             ln=1)
    
    # Ligne 3 : Recruteurs
    pdf.cell(0, 10, 
             txt=f"Recruteurs : {entretien.recruteur_secondaire} (et RH)", 
             ln=1)
    
    # Ligne 4 : Date
    pdf.cell(0, 10, 
             txt=f"Date : {entretien.date_entretien}", 
             ln=1)
    
    pdf.ln(10)  # Saute une ligne

    # ===========================================================
    # 3. SCORE GLOBAL
    # ===========================================================
    pdf.set_font("Arial", 'B', 12)  # Bold, taille 12
    score_global = stats.get('score_global', 0)  # Récupère le score (défaut 0)
    pdf.cell(0, 10, 
             txt=f"Moyenne générale : {score_global}/10", 
             ln=1)
    pdf.ln(5)  # Saute 5 pixels

    # ===========================================================
    # 4. TABLEAU DES ÉVALUATIONS - ENTÊTES
    # ===========================================================
    pdf.set_font("Arial", 'B', 10)  # Bold, taille 10
    
    # Colonne 1 : Compétence (largeur 60)
    pdf.cell(60, 7, txt="Compétence", border=1)
    
    # Colonne 2 : Note RH (largeur 25)
    pdf.cell(25, 7, txt="RH", border=1, align='C')
    
    # Colonne 3 : Note Recruteur 2 (largeur 25)
    pdf.cell(25, 7, txt="Rec. 2", border=1, align='C')
    
    # Colonne 4 : Moyenne (largeur 25)
    pdf.cell(25, 7, txt="Moyenne", border=1, align='C')
    
    # Colonne 5 : Écart (largeur 25)
    pdf.cell(25, 7, txt="Écart", border=1, align='C')
    
    pdf.ln(7)  # Passe à la ligne suivante

    # ===========================================================
    # 5. TABLEAU DES ÉVALUATIONS - LIGNES DE DONNÉES
    # ===========================================================
    pdf.set_font("Arial", size=9)  # Taille 9 pour les données
    details = stats.get('details', [])  # Récupère la liste des détails
    ecart_alerte = []
    
    for detail in details:
        # Extraction des données avec gestion des erreurs
        competence = str(detail.get('competence', ''))
        note_rh = int(detail.get('note_rh', 0))
        note_rec2 = int(detail.get('note_rec2', 0))
        moyenne = float(detail.get('moyenne', 0))
        ecart = float(detail.get('ecart', 0))
        alerte = bool(detail.get('alerte', False))  # True si écart > 2

        if alerte == True :
            ecart_alerte += competence

        # ====================================================
        # CELLULES DE LA LIGNE
        # ====================================================
        
        # Compétence (largeur 60)
        pdf.cell(60, 7, 
                 txt=competence[:30],  # Limité à 30 caractères
                 border=1, 
                 )
        
        # Note RH (largeur 25)
        pdf.cell(25, 7, 
                 txt=f"{note_rh}", 
                 border=1, 
                 align='C'
                 )
        
        # Note Recruteur 2 (largeur 25)
        pdf.cell(25, 7, 
                 txt=f"{note_rec2}", 
                 border=1, 
                 align='C' 
                 )
        
        # Moyenne (largeur 25, format à 1 décimale)
        pdf.cell(25, 7, 
                 txt=f"{moyenne:.1f}", 
                 border=1, 
                 align='C'
                 )
        
        # Écart (largeur 25, format à 1 décimale)
        pdf.cell(25, 7, 
                 txt=f"{ecart:.1f}", 
                 border=1, 
                 align='C',
                 )
        
        pdf.ln(7)  # Passe à la ligne suivante

    pdf.ln(10)  # Saute une ligne

    # ===========================================================
    # 6. LÉGENDE EN BAS DE PAGE
    # ===========================================================
    pdf.set_font("Arial", 'I', 9)  # Italique, taille 9
    pdf.cell(0, 5, 
             txt="Note : Les recruteurs ont fournit un vote avec un écart superieur à 2, pour les compétences suivantes :",
             ln=1
             )

    # ===========================================================
    # 7. RETOUR DU PDF EN BYTES
    # ===========================================================
    # dest='S' : retourne une string sans compression
    pdf_output = pdf.output(dest='S')
    
    # Convertit la string en bytes si nécessaire
    if isinstance(pdf_output, str):
        return pdf_output.encode('latin-1')
    
    return pdf_output