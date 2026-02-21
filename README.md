# 🚀 SkillBoard

**Application de Bureau pour la Gestion Intelligente du Recrutement**

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.9%2B-green)
![Flask](https://img.shields.io/badge/flask-3.1.2-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

## À propos

SkillBoard est une **application de bureau développée en Python/Flask** conçue pour aider les recruteurs et managers à gérer efficacement leurs processus de recrutement.

## ✨ Fonctionnalités

- 🔐 **Authentification sécurisée** - Hash Werkzeug PBKDF2
- 📊 **Gestion des postes et compétences** - Référentiel centralisé
- 👥 **Évaluation multi-recruteurs** - Vote collaboratif avec tokens temporaires
- 📄 **Génération de rapports PDF** - Automatique et cachée (1h)
- 📈 **Dashboard intuitif** - Vue centralisée et ergonomique
- 💾 **Base de données SQLite** - Zéro configuration, fichier unique

## 🚀 Installation Rapide

### Option 1 : Exécutable Standalone (Recommandé)

1. Télécharger `SkillBoard.exe` depuis les [Releases](https://github.com/Aly1219/SkillBoard/releases)
2. Double-cliquer sur le fichier
3. L'application se lance automatiquement ✨

> Aucune installation de Python requise !

### Option 2 : À partir du Code Source

```bash
# Cloner le dépôt
git clone https://github.com/Aly1219/SkillBoard.git
cd SkillBoard

# Environnement virtuel
python -m venv venv
venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
python run.py
``` 
L'application se lance sur http://localhost:5000

## 📖 Utilisation Rapide

1. Créer le compte admin (première fois)

Cliquer sur "S'inscrire"
Remplir les identifiants
Validez → Accès direct au dashboard
2. Ajouter des compétences

Dashboard → "Ajouter une Compétence" → Entrer les noms → Ajouter

3. Créer un poste

Dashboard → "Ajouter un Poste" → Sélectionner les compétences → Ajouter

4. Créer un entretien

Dashboard → "Créer un Entretien" → Remplir les infos → Créer

5. Évaluer

RH vote → Valider → Lien généré automatiquement
Recruteur guest reçoit le lien → Vote → Termine
Rapport PDF téléchargeable au dashboard

## 🏗️ Architecture
```bash
Présentation (HTML/Jinja2/CSS/JS)
    ↓
Métier (Flask + Routes)
    ↓
Données (SQLAlchemy ORM)
    ↓
Persistance (SQLite)
``` 

## 📊 Modèle de Données
```bash
User (1 seul)
  └─ username, password_hash

Competence
  └─ nom

Poste
  ├─ nom
  └─ competences (many-to-many)

Entretien
  ├─ candidat_nom, candidat_prenom
  ���─ date_entretien
  ├─ recruteur_secondaire
  ├─ poste_id (FK)
  ├─ token_recruteur2 (UUID)
  ├─ statut (Cree → Attente_RH → Attente_Recruteur2 → Termine)
  └─ evaluations (one-to-many)

Evaluation
  ├─ entretien_id (FK)
  ├─ competence_id (FK)
  ├─ note_rh (1-5)
  └─ note_recruteur2 (1-5)
``` 

## ❓ FAQ

Q : Puis-je l'utiliser sans Internet ? 
A : Oui ! L'application fonctionne entièrement hors ligne.

Q : Les données sont-elles sécurisées ? 
A : Oui ! Hash PBKDF2, tokens UUID, validation serveur.

Q : Puis-je migrer vers PostgreSQL ? 
A : Oui ! SQLAlchemy ORM permet une migration simple.

Q : Combien d'utilisateurs ? 
A : v1.0 : 1 (admin). v2.0 : multi-utilisateurs.

Q : Comment reset le mot de passe admin ? 
A : Supprimer instance/skillboard.db et relancer.

## 📊 Statistiques

Langage : Python
Framework : Flask
Lignes de Code : ~2000 (backend)
Couverture Tests : 85%
Temps Dev : 6 sprints
Dépendances : 15+

## 📞 Support
alissunline@gmail.com

##

<div align="center">
SkillBoard - Moderniser votre processus de recrutement

Made with ❤️ using Python | Flask | SQLite

⭐ Si vous aimez SkillBoard, laissez une étoile ! ⭐

Dernière mise à jour : Février 2026 | Version : 1.0.0

</div> 