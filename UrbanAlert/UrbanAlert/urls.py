# ==========================================
# URLS PRINCIPALES DU PROJET URBANALERT
# ==========================================

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    # Interface d'administration Django intégrée
    path('admin/', admin.site.urls),

    # Page d'accueil
    path('', include('accueil.urls')),

    # Authentification (inscription, connexion, déconnexion, profil)
    path('', include('utilisateurs.urls')),

    # Signalements (soumission, liste, détail, carte, API JSON)
    path('', include('signalements.urls')),

    # Interactions citoyennes (votes, commentaires)
    path('', include('interactions.urls')),

    # Modération administrative (statuts, modération)
    path('', include('moderation.urls')),

    # Rapports et statistiques
    path('', include('rapports.urls')),

    # Tableau de bord administrateur
    path('dashboard-admin/', include('tableau_de_bord.urls')),
]

# Servir les fichiers media en mode DEBUG
urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)