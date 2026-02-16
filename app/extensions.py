from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager() # On ajoute le LoginManager ici pour qu'il soit accessible partout sans import circulaire.