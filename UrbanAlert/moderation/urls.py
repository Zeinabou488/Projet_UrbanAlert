# ==========================================
# URLS : MODULE MODERATION
# ==========================================

from django.urls import path
from . import views

urlpatterns = [

    # Changer le statut d'un signalement
    path(
        'admin/signalements/<int:signalement_id>/statut/',
        views.changer_statut,
        name='changer_statut'
    ),

    # Modérer (supprimer/rejeter) un signalement
    path(
        'admin/signalements/<int:signalement_id>/moderer/',
        views.moderer_signalement,
        name='moderer_signalement'
    ),

    # Masquer un commentaire
    path(
        'admin/commentaires/<int:commentaire_id>/moderer/',
        views.moderer_commentaire,
        name='moderer_commentaire'
    ),
]
