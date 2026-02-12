# 🚀 SkillBoard

**SkillBoard** est une application de bureau (Desktop) développée en Python/Flask conçue pour aider les recruteurs et managers à gérer leurs processus de recrutement. Elle permet de définir des postes, d'associer des compétences, de mener des entretiens d'évaluation et de générer des rapports PDF.

L'application est conçue pour être compilée en exécutable (`.exe`) via **PyInstaller** pour une distribution simplifiée sans installation de Python requise chez le client.

---

## 📋 Fonctionnalités Clés

*   **Gestion des Postes & Compétences :** Création dynamique de fiches de poste et référentiel de compétences.
*   **Tableau de Bord (Dashboard) :** Vue d'ensemble des entretiens en cours, terminés ou en attente.
*   **Système d'Authentification Sécurisé :**
    *   Premier lancement : Initialisation du compte Administrateur.
    *   Login / Logout sécurisé.
    *   **Récupération de mot de passe** par Email (via Gmail SMTP) avec token temporaire.
*   **Architecture Modulaire :** Code organisé selon le *Factory Pattern* pour une maintenance aisée.
*   **Base de Données Locale :** SQLite (fichier unique), sans configuration serveur requise.