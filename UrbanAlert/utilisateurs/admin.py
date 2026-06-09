# Importation du module admin de Django
from django.contrib import admin


# Importation des modèles de l'application utilisateurs
from .models import Utilisateur, Role


# Enregistrement du modèle Utilisateur
# dans l'interface d'administration Django
admin.site.register(Utilisateur)


# Enregistrement du modèle Role
# dans l'interface d'administration Django
admin.site.register(Role)