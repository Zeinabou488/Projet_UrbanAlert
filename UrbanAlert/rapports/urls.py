# ==========================================
# URLS : MODULE RAPPORTS
# ==========================================

from django.urls import path
from . import views

urlpatterns = [

    # Page de statistiques
    path(
        'admin/statistiques/',
        views.statistiques,
        name='statistiques'
    ),

    # Liste des rapports archivés
    path(
        'admin/rapports/',
        views.liste_rapports,
        name='liste_rapports'
    ),

    # Générer un nouveau rapport
    path(
        'admin/rapports/generer/',
        views.generer_rapport,
        name='generer_rapport'
    ),

    # Télécharger un rapport archivé
    path(
        'admin/rapports/<int:rapport_id>/telecharger/',
        views.telecharger_rapport,
        name='telecharger_rapport'
    ),
]
