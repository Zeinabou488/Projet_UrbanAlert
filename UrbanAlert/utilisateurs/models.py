# Importation du module models de Django
# Permet de créer des tables dans la base de données
from django.db import models


# Importation du modèle utilisateur avancé de Django
# AbstractUser contient déjà :
# username, password, email, permissions, etc.
from django.contrib.auth.models import AbstractUser



# =========================
# TABLE ROLE


# Création de la table Role
# models.Model signifie que cette classe devient une table SQL
class Role(models.Model):

    # Champ nom du rôle
    # CharField = texte court
    # max_length=50 -> taille maximale de 50 caractères
    # unique=True -> deux rôles ne peuvent pas avoir le même nom
    nom = models.CharField(
        max_length=50,
        unique=True
    )

    # Méthode spéciale utilisée pour afficher l'objet
    # Exemple :
    # au lieu d'afficher "Role object(1)"
    # Django affichera "Administrateur"
    def __str__(self):

        # Retourne le nom du rôle
        return self.nom




# =========================
# TABLE UTILISATEUR
# =========================

# Utilisateur hérite du système utilisateur Django
# On récupère automatiquement :
# username
# password
# email
# permissions
# login
# superuser
# etc.
class Utilisateur(AbstractUser):


    # =========================
    # CHAMP TELEPHONE
    # =========================

    # CharField = champ texte court
    telephone = models.CharField(

        # Taille maximale du numéro
        max_length=20,

        # blank=True
        # autorise le champ vide dans les formulaires Django
        blank=True,

        # null=True
        # autorise la valeur NULL dans PostgreSQL
        null=True
    )



    # =========================
    # PHOTO DE PROFIL
    # =========================

    # ImageField permet d'enregistrer une image
    photo_profil = models.ImageField(

        # upload_to='profils/'
        # dossier où les images seront enregistrées
        # chemin final :
        # media/profils/
        upload_to='profils/',

        # champ facultatif dans les formulaires
        blank=True,

        # autorise NULL dans la base
        null=True
    )



    # =========================
    # RELATION AVEC ROLE
    # =========================

    # ForeignKey = relation plusieurs-vers-un
    # Plusieurs utilisateurs peuvent avoir le même rôle
    role = models.ForeignKey(

        # Table liée
        Role,

        # SET_NULL :
        # si le rôle est supprimé
        # le champ role devient NULL
        on_delete=models.SET_NULL,

        # le rôle peut être vide dans la base
        null=True,

        # le rôle peut être vide dans les formulaires
        blank=True
    )



    # =========================
    # DATE DE CREATION
    # =========================

    # DateTimeField = stocke date + heure
    date_creation = models.DateTimeField(

        # auto_now_add=True
        # ajoute automatiquement la date lors de la création
        auto_now_add=True
    )



    # =========================
    # AFFICHAGE UTILISATEUR
    # =========================

    # Méthode d'affichage de l'utilisateur
    def __str__(self):

        # retourne le username de Django
        return self.username