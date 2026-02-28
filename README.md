# 🎯 SkillBoard

> **Plateforme intelligente de gestion des entretiens d'embauche**

[![Tests](https://github.com/Aly1219/SkillBoard/actions/workflows/tests.yml/badge.svg)](https://github.com/Aly1219/SkillBoard/actions)
[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
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

- 🔐 **Authentification sécurisée** - Hash PBKDF2
- 👥 **Gestion des entretiens** - Création et suivi
- 📊 **Évaluation multi-recruteurs** - Vote collaboratif
- 📄 **Génération de PDFs** - Automatique
- 🎨 **Interface moderne** - Responsive et intuitive
- 💾 **SQLite** - Zéro configuration

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

---

## 📖 Utilisation

### 1️⃣ Première connexion
- Allez sur http://localhost:5000
- Cliquez sur "S'inscrire"
- Créez votre compte admin
- Accès direct au dashboard ✨

### 2️⃣ Préparez les données
- Dashboard → Ajouter une Compétence
- Dashboard → Ajouter un Poste (sélectionner les compétences)

### 3️⃣ Créez un entretien
- Dashboard → Créer un Entretien
- Remplissez les infos du candidat
- Sélectionnez le poste
- Créer

### 4️⃣ Évaluez
- Recruteur principal → Note les compétences → Valide
- Un lien est généré pour le recruteur guest
- Recruteur guest → Reçoit le lien → Vote

### 5️⃣ Récupérez le rapport
- Dashboard → Cliquez sur l'entretien
- Bouton "Télécharger PDF"
- Rapport complet généré ! 📄

---

## 🏗️ Architecture

### Stack Technique
```
Frontend (HTML/Jinja/CSS/JS) ↔ Backend (Flask) ↔ Database (SQLite)
```

### Structure du Projet
```
SkillBoard/
├── app/
│   ├── models.py           # ORM SQLAlchemy
│   ├── routes.py           # Routes principales
│   ├── api/                # APIs
│   ├── calculs.py          # Formules statistiques
│   ├── pdf.py              # Génération PDFs
│   └── templates/          # HTML
├── tests/
│   ├── test_unitaire_*.py  # 29 tests unitaires
│   └── test_integration_*.py # 27 tests intégration
├── requirements.txt
└── run.py
```

### Modèle de Données
- **User** : Utilisateur principal
- **Competence** : Liste des compétences
- **Poste** : Postes avec compétences associées
- **Entretien** : Entretiens avec candidats
- **Evaluation** : Notes pour chaque compétence

---

## ✅ Tests & Qualité

### 57 Tests Automatisés ✅
- 📊 **Couverture** : 70%
- ⏱️ **Durée** : 8.71s
- 🔄 **CI/CD** : GitHub Actions (automatique)

### Exécuter les tests
```bash
# Tous les tests
pytest tests/ -v

# Avec couverture
pytest tests/ --cov=app --cov-report=html
```

---

## 📝 Licence

MIT License - Voir [LICENSE](LICENSE)

---

**Fait avec ❤️ par Alisson Calovini**