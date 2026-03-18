# 🎯 SkillBoard

> **Plateforme intelligente de gestion des entretiens d'embauche**

[![Tests](https://github.com/Aly1219/SkillBoard/actions/workflows/tests.yml/badge.svg)](https://github.com/Aly1219/SkillBoard/actions)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Flask 3.1+](https://img.shields.io/badge/Flask-3.1%2B-lightgrey?logo=flask)](https://flask.palletsprojects.com/)
[![SQLAlchemy 2.0](https://img.shields.io/badge/SQLAlchemy-2.0-red)](https://www.sqlalchemy.org/)
[![Coverage 70%](https://img.shields.io/badge/coverage-70%25-brightgreen)](https://github.com/Aly1219/SkillBoard)
[![Licence MIT](https://img.shields.io/badge/licence-MIT-green)](LICENSE)

---

## 📚 Table des matières

- [À propos](#-à-propos)
- [Fonctionnalités](#-fonctionnalités)
- [Installation](#-installation)
- [Utilisation](#-utilisation)
- [Architecture](#-architecture)
- [Tests](#-tests)

---

## 💡 À propos

**SkillBoard** est une application web moderne pour gérer l'intégralité de vos processus de recrutement. Interface intuitive et outils collaboratifs pour simplifier l'évaluation des candidats.

---

## ✨ Fonctionnalités

- 🔐 **Authentification sécurisée** — Hash PBKDF2
- 👥 **Gestion des entretiens** — Création et suivi
- 📊 **Évaluation multi-recruteurs** — Vote collaboratif avec lien externe
- 📄 **Rapport d'entretien** — Graphiques et analyses
- 🎨 **Interface moderne** — Responsive et intuitive
- 💾 **SQLite** — Zéro configuration

---

## 🚀 Installation

### À partir du code source

```bash
# Cloner le projet
git clone https://github.com/Aly1219/SkillBoard.git
cd SkillBoard

# Créer l'environnement virtuel
python -m venv venv

# Linux/Mac
source venv/bin/activate

# Windows
venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
python run.py
```

L'app sera accessible sur **http://localhost:5000**

### Avec Docker

```bash
docker build -t skillboard .
docker run -p 5000:5000 skillboard
```

---

## 📖 Utilisation

### 1️⃣ Première connexion
- Allez sur http://localhost:5000
- Créez votre compte administrateur (première visite uniquement)
- Accès direct au dashboard ✨

### 2️⃣ Préparez les données
- Dashboard → Ajouter une Compétence
- Dashboard → Ajouter un Poste (sélectionner les compétences)

### 3️⃣ Créez un entretien
- Dashboard → Créer un Entretien
- Remplissez les infos du candidat
- Sélectionnez le poste et confirmez

### 4️⃣ Évaluez
- Recruteur principal → Note les compétences → Valide
- Un lien est généré automatiquement pour le recruteur externe
- Recruteur externe → Reçoit le lien → Vote depuis son navigateur

### 5️⃣ Récupérez le rapport
- Dashboard → Bouton "Rapport" sur l'entretien terminé
- Rapport complet avec graphiques et analyse des écarts 📄

---

## 🏗️ Architecture

### Stack Technique
```
Frontend (HTML / Jinja2 / CSS / JS) ↔ Backend (Flask) ↔ Database (SQLite)
```

### Structure du Projet
```
SkillBoard/
├── app/
│   ├── models.py           # Modèles SQLAlchemy
│   ├── routes.py           # Routes principales
│   ├── api/                # Blueprint API REST
│   ├── calculs.py          # Logique métier — statistiques
│   ├── db_helpers.py       # Requêtes centralisées (DRY)
│   ├── validators.py       # Validateurs réutilisables
│   ├── utils.py            # Utilitaires (chemins, formatage)
│   ├── extensions.py       # Instances Flask extensions
│   └── templates/          # Templates HTML (Jinja2)
├── tests/
│   ├── conftest.py               # Fixtures partagées
│   ├── test_unitaire_*.py        # Tests unitaires
│   └── test_integration_*.py    # Tests d'intégration
├── config.py               # Configurations dev/prod/test
├── requirements.txt
├── Dockerfile
└── run.py
```

### Modèle de Données
- **User** — Compte administrateur
- **Competence** — Compétences évaluables
- **Poste** — Postes avec compétences associées (many-to-many)
- **Entretien** — Entretien lié à un candidat et un poste
- **Evaluation** — Note par compétence (RH + recruteur externe)

---

## ✅ Tests & Qualité

### Couverture automatisée
- 📊 **Couverture** : 70%
- ⏱️ **Durée** : ~9s
- 🔄 **CI/CD** : GitHub Actions (automatique à chaque push)

### Exécuter les tests

```bash
# Tous les tests
pytest

# Avec rapport de couverture HTML
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

---

## 📝 Licence

MIT License — Voir [LICENSE](LICENSE)

---

**Fait avec ❤️ par Alisson Calovini**