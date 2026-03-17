# ============================================================
# TABLE DES MATIÈRES
# 1.  CONSTANTES
# 2.  calculer_stat()   — statistiques complètes d'un entretien
# ============================================================

# ============================================================
# 1. CONSTANTES
# ============================================================
PALIER_DEFAUT = 7  # Note minimale requise par défaut si non définie


# ============================================================
# 2. CALCUL DES STATISTIQUES
# ============================================================
def calculer_stat(evaluations):
    """
    Calcule les statistiques complètes à partir des évaluations d'un entretien.

    Args:
        evaluations: liste d'objets Evaluation (SQLAlchemy)

    Returns:
        dict avec les clés :
            details, details_tries, moy_generale, palier_moyen,
            meilleure_competence, meilleure_note,
            pire_competence, pire_note,
            competences_sous_palier, nombre_sous_palier, pourcentage_sous_palier
    """
    if not evaluations:
        return {
            "details": [],
            "details_tries": [],
            "moy_generale": 0,
            "palier_moyen": 0,
            "meilleure_competence": "N/A",
            "meilleure_note": 0,
            "pire_competence": "N/A",
            "pire_note": 0,
            "competences_sous_palier": [],
            "nombre_sous_palier": 0,
            "pourcentage_sous_palier": 0,
        }

    resultats = []
    total_moyenne = 0

    for eva in evaluations:
        n1 = eva.note_rh or 0
        n2 = eva.note_recruteur2 or 0
        moyenne = (n1 + n2) / 2
        palier = eva.palier or PALIER_DEFAUT

        atteint_palier = moyenne >= palier
        ecart_palier   = moyenne - palier   # positif = au-dessus du palier
        ecart_votes    = abs(n1 - n2)       # divergence entre les deux recruteurs

        resultats.append({
            "competence":    eva.competence.nom,
            "note_rh":       n1,
            "note_rec2":     n2,
            "moyenne":       moyenne,
            "ecart":         palier - moyenne,  # négatif = objectif atteint
            "ecart_votes":   ecart_votes,
            "atteint_palier": atteint_palier,
            "ecart_palier":  ecart_palier,
            "palier":        palier,
            # alerte_recr : True si les deux recruteurs divergent
            "alerte_recr":   ecart_votes > 0,
        })

        total_moyenne += moyenne

    count = len(resultats)

    moy_generale  = total_moyenne / count
    meilleure     = max(resultats, key=lambda x: x['moyenne'])
    pire          = min(resultats, key=lambda x: x['moyenne'])
    sous_palier   = [r for r in resultats if not r['atteint_palier']]
    resultats_tries = sorted(resultats, key=lambda x: x['moyenne'], reverse=True)
    palier_moyen  = sum(r['palier'] for r in resultats) / count

    return {
        "details":        resultats,
        "details_tries":  resultats_tries,
        "moy_generale":   round(moy_generale, 2),
        "palier_moyen":   round(palier_moyen, 2),

        "meilleure_competence": meilleure['competence'],
        "meilleure_note":       round(meilleure['moyenne'], 2),

        "pire_competence": pire['competence'],
        "pire_note":       round(pire['moyenne'], 2),

        "competences_sous_palier":  sous_palier,
        "nombre_sous_palier":       len(sous_palier),
        "pourcentage_sous_palier":  round((len(sous_palier) / count) * 100, 1),
    }