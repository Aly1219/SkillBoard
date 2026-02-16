import sys
import os

def resource_path(relative_path):
    """Retourne le chemin absolu, que l'on soit en dev ou dans un bundle PyInstaller"""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)
