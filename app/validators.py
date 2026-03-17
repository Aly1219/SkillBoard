"""
Validateurs réutilisables pour l'application.
Centralise la logique de validation pour respecter le principe DRY.

Toutes les fonctions retournent un tuple (is_valid: bool, error_message: str | None).
"""

# ============================================================
# TABLE DES MATIÈRES
# 1.  CHAMPS GÉNÉRIQUES     string / liste
# 2.  EXISTENCE             compétence / poste / entretien
# 3.  STATUT D'ENTRETIEN    not_finished / waiting_for_recruiter2
# 4.  NOTES                 validate_note_range
# ============================================================


# ============================================================
# 1. CHAMPS GÉNÉRIQUES
# ============================================================

def validate_string_field(value, field_name="champ"):
    """
    Valide qu'un champ string n'est pas vide.

    Args:
        value:      Valeur à valider
        field_name: Nom du champ (pour le message d'erreur)

    Returns:
        tuple: (is_valid, error_message)
    """
    if not value or not value.strip():
        return False, f"Le {field_name} est requis"
    return True, None


def validate_not_empty_list(items, list_name="éléments"):
    """
    Valide qu'une liste n'est pas vide.

    Args:
        items:     Liste à valider
        list_name: Nom de la liste (pour le message d'erreur)

    Returns:
        tuple: (is_valid, error_message)
    """
    if not items:
        return False, f"Au moins un {list_name} est requis"
    return True, None


# ============================================================
# 2. EXISTENCE
# ============================================================

def validate_skill_exists(competence, skill_name=""):
    """Valide qu'une compétence existe en base"""
    if not competence:
        return False, f"Compétence non trouvée : {skill_name}"
    return True, None


def validate_poste_exists(poste, poste_name=""):
    """Valide qu'un poste existe en base"""
    if not poste:
        return False, f"Poste non trouvé : {poste_name}"
    return True, None


def validate_entretien_exists(entretien, entretien_id=""):
    """Valide qu'un entretien existe en base"""
    if not entretien:
        return False, f"Entretien non trouvé : {entretien_id}"
    return True, None


# ============================================================
# 3. STATUT D'ENTRETIEN
# ============================================================

def validate_entretien_not_finished(entretien):
    """Valide qu'un entretien n'est pas encore terminé"""
    if entretien.statut == "Termine":
        return False, "Cet entretien est déjà clôturé"
    return True, None


def validate_entretien_waiting_for_recruiter2(entretien):
    """Valide que l'entretien est bien en attente du 2e recruteur"""
    if entretien.statut != "Attente_Recruteur2":
        return False, f"Cet entretien n'est pas en attente d'évaluation (statut : {entretien.statut})"
    return True, None


# ============================================================
# 4. NOTES
# ============================================================

def validate_note_range(note, min_val=1, max_val=10):
    """
    Valide qu'une note est présente et dans la plage acceptée.

    Args:
        note:    Valeur à valider (str ou int)
        min_val: Valeur minimale acceptée (défaut : 1)
        max_val: Valeur maximale acceptée (défaut : 10)

    Returns:
        tuple: (is_valid, error_message)
    """
    # Guard : valeur absente ou vide
    if note is None or str(note).strip() == "":
        return False, "Note manquante"

    try:
        note_int = int(note)
        if note_int < min_val or note_int > max_val:
            return False, f"La note doit être entre {min_val} et {max_val}"
        return True, None
    except (ValueError, TypeError):
        return False, "La note doit être un nombre entier"