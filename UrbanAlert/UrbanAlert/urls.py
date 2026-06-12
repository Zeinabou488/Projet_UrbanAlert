# ==========================================
# URLS PRINCIPALES DU PROJET URBANALERT
# ==========================================

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [

    # Rapports et statistiques (avant admin pour que les URLs admin/* soient trouvées)
    path('', include('rapports.urls')),

    # Interface d'administration Django intégrée
    path('admin/', admin.site.urls),

    # Page d'accueil
    path('', include('accueil.urls')),

    # Authentification (inscription, connexion, déconnexion, profil)
    path('', include('utilisateurs.urls')),

    # Signalements (soumission, liste, détail, carte, API JSON)
    path('', include('signalements.urls')),
0
    # Interactions citoyennes (votes, commentaires)
    path('', include('interactions.urls')),

    # Modération administrative (statuts, modération)
    path('', include('moderation.urls')),

    # Tableau de bord administrateur
    path('dashboard-admin/', include('tableau_de_bord.urls')),
]

# Servir les fichiers media en mode DEBUG
urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)