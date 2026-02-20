from fpdf import FPDF
import io

def generer_rapport(entretien, stats) -> bytes:
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, txt=f"Rapport d'Entretien : {entretien.candidat_nom} {entretien.candidat_prenom}", ln=1, align='C')
    pdf.ln(10)

    pdf.set_font("Arial", size=11)
    pdf.cell(0, 10, txt=f"Candidat : {entretien.candidat_nom} {entretien.candidat_prenom}", ln=1)
    pdf.cell(0, 10, txt=f"Poste : {entretien.poste.nom}", ln=1)
    pdf.cell(0, 10, txt=f"Recruteurs : {entretien.recruteur_secondaire} (et RH)", ln=1)
    pdf.ln(10)

    # ... tableau résultats avec stats ...

    # Retourne le PDF en bytes (pas de fichier)
    pdf_str = pdf.output(dest="S")          # str (latin-1) avec fpdf
    return pdf_str.encode("latin-1")
