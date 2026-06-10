# ==========================================
# VUES : PAGE D'ACCUEIL
# Affiche les statistiques globales
# et les derniers signalements
# ==========================================

from django.shortcuts import render
from django.db.models import Count


def accueil(request):
    """
    Page d'accueil avec :
    - Statistiques globales (total, résolus, urgences)
    - 6 derniers signalements les plus votés
    - Catégories disponibles
    """

    # Import conditionnel pour éviter les erreurs si migrations pas encore faites
    try:
        from signalements.models import Signalement, CategorieProbleme

        total = Signalement.objects.count()
        resolus = Signalement.objects.filter(statut__code='resolu').count()
        urgences = Signalement.objects.filter(est_urgence=True).exclude(
            statut__code='resolu'
        ).count()

        derniers = Signalement.objects.select_related(
            'sous_categorie__categorie',
            'quartier__commune',
            'statut'
        ).annotate(nb_votes=Count('votes')).order_by(
            '-est_urgence', '-nb_votes', '-date_creation'
        )[:6]

        categories = CategorieProbleme.objects.all()[:9]

        taux = round((resolus / total * 100) if total > 0 else 0, 1)

    except Exception:
        total = resolus = urgences = taux = 0
        derniers = []
        categories = []

    context = {
        'total': total,
        'resolus': resolus,
        'urgences': urgences,
        'taux': taux,
        'derniers': derniers,
        'categories': categories,
    }
    return render(request, 'accueil/index.html', context)
