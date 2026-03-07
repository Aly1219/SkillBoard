def calculer_stat(evaluations):
    """
    Reçoit la liste des évaluations.
    Retourne un dictionnaire avec le détail par compétence et le score global.
    """
    resultats = []
    total_moyenne = 0
    count = 0
    
    for eva in evaluations:
        n1 = eva.note_rh or 0
        n2 = eva.note_recruteur2 or 0
        
        moyenne = (n1 + n2) / 2
        ecart = abs(n1 - n2)
        
        resultats.append({
            "competence": eva.competence.nom,
            "note_rh": n1,
            "note_rec2": n2,
            "moyenne": moyenne,
            "ecart": ecart,
            "alerte": ecart > 2 # Vrai si écart > 2
        })
        
        total_moyenne += moyenne
        count += 1
        
    score_global = total_moyenne / count if count > 0 else 0
    
    return {
        "details": resultats,
        "score_global": round(score_global, 2)
    }
