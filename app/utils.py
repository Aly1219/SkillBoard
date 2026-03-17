import sys
import os
from datetime import datetime

# ============================================================
# TABLE DES MATIÈRES
# 1.  resource_path()    — chemins compatibles PyInstaller
# 2.  format_date_fr()   — formatage de date en français
# ============================================================

# ============================================================
# 1. CHEMINS
# ============================================================
def resource_path(relative_path):
    """
    Retourne le chemin absolu vers une ressource.
    Compatible développement et bundle PyInstaller (_MEIPASS).
    """
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


# ============================================================
# 2. FORMATAGE DE DATE
# ============================================================
_MOIS_FR = {
    1: "janvier",  2: "février",  3: "mars",
    4: "avril",    5: "mai",      6: "juin",
    7: "juillet",  8: "août",     9: "septembre",
    10: "octobre", 11: "novembre", 12: "décembre",
}

def format_date_fr(date_entretien):
    """
    Convertit une date en chaîne lisible en français.

    Accepte :
        - un objet datetime.date  → directement formaté
        - une chaîne 'YYYY-MM-DD' → parsée puis formatée

    Retourne :
        str  ex. "31 janvier 2026"
             ou la valeur originale si le format est invalide
    """
    if date_entretien is None:
        return ""

    # Cas 1 : objet date natif (après migration vers db.Date)
    if hasattr(date_entretien, 'day'):
        return f"{date_entretien.day} {_MOIS_FR[date_entretien.month]} {date_entretien.year}"

    # Cas 2 : chaîne ISO (données existantes avant migration)
    try:
        date_obj = datetime.strptime(str(date_entretien), '%Y-%m-%d')
        return f"{date_obj.day} {_MOIS_FR[date_obj.month]} {date_obj.year}"
    except ValueError:
        return str(date_entretien)  # Format inconnu — on retourne tel quel