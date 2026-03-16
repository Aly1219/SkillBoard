"""
Validateurs réutilisables pour l'application
Centralise la logique de validation pour respecter le DRY
"""


def validate_string_field(value, field_name="champ"):
    """
    Valide qu'un champ string n'est pas vide
    
    Args:
        value: Valeur à valider
        field_name: Nom du champ (pour le message d'erreur)
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not value or not value.strip():
        return False, f"Le {field_name} est requis"
    return True, None


def validate_not_empty_list(items, list_name="éléments"):
    """
    Valide qu'une liste n'est pas vide
    
    Args:
        items: Liste à valider
        list_name: Nom de la liste (pour le message d'erreur)
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not items or len(items) == 0:
        return False, f"Au moins un {list_name} est requis"
    return True, None


def validate_skill_exists(competence, skill_name=""):
    """Valide qu'une compétence existe"""
    if not competence:
        return False, f"Compétence non trouvée: {skill_name}"
    return True, None


def validate_poste_exists(poste, poste_name=""):
    """Valide qu'un poste existe"""
    if not poste:
        return False, f"Poste non trouvé: {poste_name}"
    return True, None


def validate_entretien_exists(entretien, entretien_id=""):
    """Valide qu'un entretien existe"""
    if not entretien:
        return False, f"Entretien non trouvé: {entretien_id}"
    return True, None


def validate_entretien_not_finished(entretien):
    """Valide qu'un entretien n'est pas terminé"""
    if entretien.statut == "Termine":
        return False, "Cet entretien est déjà clôturé"
    return True, None


def validate_entretien_waiting_for_recruiter2(entretien):
    """Valide que l'entretien attend le 2e recruteur"""
    if entretien.statut != "Attente_Recruteur2":
        return False, f"Cet entretien n'est pas en attente d'évaluation (statut: {entretien.statut})"
    return True, None


def validate_note_range(note, min_val=1, max_val=10):
    """Valide qu'une note est dans la plage acceptée"""
    try:
        note_int = int(note)
        if note_int < min_val or note_int > max_val:
            return False, f"La note doit être entre {min_val} et {max_val}"
        return True, None
    except (ValueError, TypeError):
        return False, "La note doit être un nombre"