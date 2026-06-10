# ==========================================
# URLS : TABLEAU DE BORD ADMINISTRATEUR
# ==========================================

from django.urls import path
from . import views

urlpatterns = [

    # Dashboard principal
    path('', views.dashboard_admin, name='dashboard_admin'),

    # Liste et gestion des signalements
    path('signalements/', views.dashboard_signalements, name='dashboard_signalements'),
    path('signalements/<int:pk>/', views.detail_signalement_admin, name='detail_signalement_admin'),

    # Gestion des utilisateurs
    path('utilisateurs/', views.liste_utilisateurs, name='liste_utilisateurs'),
    path('utilisateurs/supprimer/<int:user_id>/', views.supprimer_utilisateur, name='supprimer_utilisateur'),
    path('utilisateurs/reactiver/<int:user_id>/', views.reactiver_utilisateur, name='reactiver_utilisateur'),
    path('utilisateurs/modifier/<int:user_id>/', views.modifier_utilisateur, name='modifier_utilisateur'),
]