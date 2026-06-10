# ==========================================
# URLS : MODULE SIGNALEMENTS
# ==========================================

from django.urls import path
from . import views

urlpatterns = [

    # Soumission d'un nouveau signalement
    path(
        'signaler/',
        views.soumettre_signalement,
        name='soumettre_signalement'
    ),

    # Liste publique des signalements
    path(
        'signalements/',
        views.liste_signalements,
        name='liste_signalements'
    ),

    # Détail d'un signalement
    path(
        'signalements/<int:pk>/',
        views.detail_signalement,
        name='detail_signalement'
    ),

    # Espace personnel citoyen
    path(
        'mes-signalements/',
        views.mes_signalements,
        name='mes_signalements'
    ),

    # Carte interactive
    path(
        'carte/',
        views.carte_signalements,
        name='carte_signalements'
    ),

    # API JSON pour la carte
    path(
        'api/signalements/',
        views.api_signalements_json,
        name='api_signalements_json'
    ),

    # API JSON sous-catégories (formulaire dynamique)
    path(
        'api/sous-categories/<int:categorie_id>/',
        views.api_sous_categories,
        name='api_sous_categories'
    ),

    # API JSON quartiers (formulaire dynamique)
    path(
        'api/quartiers/<int:commune_id>/',
        views.api_quartiers,
        name='api_quartiers'
    ),
]
