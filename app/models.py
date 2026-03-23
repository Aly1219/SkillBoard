from app.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# ============================================================
# TABLE DES MATIÈRES
# 1.  TABLE D'ASSOCIATION   poste_competence
# 2.  MODÈLE Competence
# 3.  MODÈLE Poste
# 4.  MODÈLE Entretien
# 5.  MODÈLE Evaluation
# 6.  MODÈLE User
# ============================================================


# ============================================================
# 1. TABLE D'ASSOCIATION — relation many-to-many Poste ↔ Competence
# ============================================================
poste_competence = db.Table('poste_competence',
    db.Column('poste_id',      db.Integer, db.ForeignKey('poste.id'),      primary_key=True),
    db.Column('competence_id', db.Integer, db.ForeignKey('competence.id'), primary_key=True)
)


# ============================================================
# 2. COMPÉTENCE
# ============================================================
class Competence(db.Model):
    id  = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    __table_args__ = (db.UniqueConstraint('nom', name='uq_competence_nom'),)

    def __repr__(self):
        return f"<Competence {self.nom!r}>"


# ============================================================
# 3. POSTE
# ============================================================
class Poste(db.Model):
    id  = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    __table_args__ = (db.UniqueConstraint('nom', name='uq_poste_nom'),)
    competences = db.relationship(
        'Competence',
        secondary=poste_competence,
        lazy='subquery',
        backref=db.backref('postes', lazy=True)
    )

    def __repr__(self):
        return f"<Poste {self.nom!r}>"


# ============================================================
# 4. ENTRETIEN
# ============================================================
class Entretien(db.Model):
    id                  = db.Column(db.Integer, primary_key=True)
    candidat_nom        = db.Column(db.String(50))
    candidat_prenom     = db.Column(db.String(50))
    # db.Date stocke une vraie date → tri natif, pas de bug de format
    date_entretien      = db.Column(db.Date)
    recruteur_secondaire = db.Column(db.String(50))
    poste_id            = db.Column(db.Integer, db.ForeignKey('poste.id'))
    poste               = db.relationship('Poste', backref='entretiens')
    # PIN à 6 chiffres pour le second recruteur — stocké hashé (PBKDF2)
    pin_hash            = db.Column(db.String(200), nullable=True)
    statut              = db.Column(db.String(20), default="Cree")
    evaluations         = db.relationship('Evaluation', backref='entretien', lazy=True)

    def set_pin(self, pin):
        """Hash et stocke le PIN avec PBKDF2 (même mécanisme que les mots de passe)"""
        self.pin_hash = generate_password_hash(str(pin))

    def check_pin(self, pin):
        """Vérifie le PIN saisi contre le hash stocké"""
        if not self.pin_hash:
            return False
        return check_password_hash(self.pin_hash, str(pin))

    def clear_pin(self):
        """Invalide le PIN après usage"""
        self.pin_hash = None

    def __repr__(self):
        return f"<Entretien {self.candidat_nom} {self.candidat_prenom} — {self.date_entretien}>"


# ============================================================
# 5. ÉVALUATION
# ============================================================
class Evaluation(db.Model):
    id              = db.Column(db.Integer, primary_key=True)
    entretien_id    = db.Column(db.Integer, db.ForeignKey('entretien.id'), nullable=False)
    competence_id   = db.Column(db.Integer, db.ForeignKey('competence.id'), nullable=False)
    note_rh         = db.Column(db.Integer, nullable=True)
    note_recruteur2 = db.Column(db.Integer, nullable=True)
    palier          = db.Column(db.Integer)
    ponderation     = db.Column(db.Integer)
    competence      = db.relationship('Competence')

    def __repr__(self):
        return f"<Evaluation entretien={self.entretien_id} competence={self.competence_id}>"


# ============================================================
# 6. UTILISATEUR
# ============================================================
class User(UserMixin, db.Model):
    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        """Crée le hash du mot de passe avant stockage"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Vérifie le mot de passe contre le hash stocké"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username!r}>"