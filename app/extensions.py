from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail

db = SQLAlchemy()
login_manager = LoginManager() # On ajoute le LoginManager ici pour qu'il soit accessible partout sans import circulaire.
mail = Mail()