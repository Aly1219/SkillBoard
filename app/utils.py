import sys
import os
import socket
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
    if date_entretien is None:
        return ""

    # Cas 1 : objet date ou datetime natif Python
    if hasattr(date_entretien, 'strftime'):
        return f"{date_entretien.day} {_MOIS_FR[date_entretien.month]} {date_entretien.year}"

    # Cas 2 : chaîne ISO "YYYY-MM-DD" (données avant migration)
    try:
        date_obj = datetime.strptime(str(date_entretien), '%Y-%m-%d')
        return f"{date_obj.day} {_MOIS_FR[date_obj.month]} {date_obj.year}"
    except ValueError:
        return str(date_entretien)

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return '127.0.0.1'