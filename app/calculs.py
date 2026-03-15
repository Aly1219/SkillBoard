def calculer_stat(evaluations):
    """
    Calcule les statistiques des évaluations
    Le palier vient de chaque Evaluation
    """
    resultats = []
    total_moyenne = 0
    count = 0
    
    for eva in evaluations:
        n1 = eva.note_rh or 0
        n2 = eva.note_recruteur2 or 0
        
        moyenne = (n1 + n2) / 2
        ecart_moy_pal = eva.palier - moyenne
        ecart_rec = abs(n1 - n2)
        palier = eva.palier or 0
        
        atteint_palier = moyenne >= palier
        ecart_palier = moyenne - palier
        
        resultats.append({
            "competence": eva.competence.nom,
            "note_rh": n1,
            "note_rec2": n2,
            "moyenne": moyenne,
            "ecart": ecart_moy_pal,
            "ecart_votes": ecart_rec,
            "alerte": ecart_palier > 0,
            "alerte_recr": ecart_rec > 0,
            "atteint_palier": atteint_palier,
            "ecart_palier": ecart_palier,
            "palier": palier
        })
        
        total_moyenne += moyenne
        count += 1
    
    # ====================================================
    # ANALYSES COMPLÉMENTAIRES
    # ====================================================
    moy_generale = total_moyenne / count if count > 0 else 0
    
    meilleure = max(resultats, key=lambda x: x['moyenne'])
    pire = min(resultats, key=lambda x: x['moyenne'])
    
    sous_palier = [r for r in resultats if not r['atteint_palier']]
    resultats_tries = sorted(resultats, key=lambda x: x['moyenne'], reverse=True)
    
    # ✅ Palier moyen (pour les recommandations)
    palier_moyen = sum([r['palier'] for r in resultats]) / len(resultats) if resultats else 7
    
    return {
        "details": resultats,
        "details_tries": resultats_tries,
        "moy_generale": round(moy_generale, 2),
        "palier_moyen": palier_moyen,
        
        "meilleure_competence": meilleure['competence'],
        "meilleure_note": round(meilleure['moyenne'], 2),
        
        "pire_competence": pire['competence'],
        "pire_note": round(pire['moyenne'], 2),
        
        "competences_sous_palier": sous_palier,
        "nombre_sous_palier": len(sous_palier),
        "pourcentage_sous_palier": round((len(sous_palier) / count) * 100, 1) if count > 0 else 0,
    }