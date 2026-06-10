# ==========================================
# URLS : MODULE INTERACTIONS
# ==========================================

from django.urls import path
from . import views

urlpatterns = [

    # Vote sur un signalement
    path(
        'signalements/<int:signalement_id>/voter/',
        views.voter,
        name='voter'
    ),

    # Ajouter un commentaire
    path(
        'signalements/<int:signalement_id>/commenter/',
        views.ajouter_commentaire,
        name='ajouter_commentaire'
    ),

    # Supprimer un commentaire
    path(
        'commentaires/<int:commentaire_id>/supprimer/',
        views.supprimer_commentaire,
        name='supprimer_commentaire'
    ),
]
