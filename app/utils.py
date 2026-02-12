import sys
import os
from flask_mail import Message
from app.extensions import mail
from flask import url_for, current_app
from threading import Thread

def resource_path(relative_path):
    """Retourne le chemin absolu, que l'on soit en dev ou dans un bundle PyInstaller"""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def send_async_email(app, msg):
    """Envoi asynchrone utilisant l'instance mail globale"""
    with app.app_context():
        mail.send(msg)

def send_reset_email(user):
    """Prépare l'email et lance le thread d'envoi"""
    token = user.get_reset_token()
    
    msg = Message('Réinitialisation de votre mot de passe - SkillBoard',
                  recipients=[user.email])
                  
    reset_url = url_for('main.reset_token', token=token, _external=True)
    
    msg.body = f'''Bonjour {user.username},

Vous avez demandé à réinitialiser votre mot de passe.
Votre nom d'utilisateur est : {user.username}

Pour choisir un nouveau mot de passe, cliquez sur le lien suivant :
{reset_url}

Si vous n'êtes pas à l'origine de cette demande, ignorez simplement cet email.
'''
    # On revient à la version simple : on passe juste l'app et le message
    Thread(target=send_async_email, args=(current_app._get_current_object(), msg)).start()
