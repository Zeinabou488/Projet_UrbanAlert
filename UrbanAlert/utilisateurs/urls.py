# ==========================================
# URLS : MODULE UTILISATEURS
# ==========================================

from django.urls import path
from . import views

urlpatterns = [

    # Inscription
    path('inscription/', views.inscription_view, name='inscription'),

    # Connexion
    path('connexion/', views.connexion_view, name='connexion'),

    # Déconnexion
    path('deconnexion/', views.deconnexion_view, name='deconnexion'),

    # Profil personnel
    path('profil/', views.profil_view, name='profil'),

    # Changer le mot de passe
    path('profil/changer-mdp/', views.changer_mot_de_passe_view, name='changer_mot_de_passe'),
]