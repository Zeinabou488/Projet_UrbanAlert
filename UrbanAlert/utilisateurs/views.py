# ==========================================
# IMPORTATIONS DJANGO
# ==========================================

# render :
# afficher un template HTML
#
# redirect :
# rediriger vers une autre page
from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash

from .forms import InscriptionForm, ConnexionForm, ProfilForm



# ==========================================
# INSCRIPTION UTILISATEUR
# ==========================================

@never_cache
def inscription_view(request):

    """
    Vue inscription utilisateur
    """

    # --------------------------------------
    # SI FORMULAIRE ENVOYE
    # --------------------------------------

    if request.method == 'POST':

        form = InscriptionForm(

            request.POST,

            request.FILES
        )

        # ----------------------------------
        # SI FORMULAIRE VALIDE
        # ----------------------------------

        if form.is_valid():

            # Sauvegarde utilisateur
            form.save()

            # Redirection connexion
            return redirect(

                'connexion'
            )

    # --------------------------------------
    # FORMULAIRE VIDE
    # --------------------------------------

    else:

        form = InscriptionForm()

    # --------------------------------------
    # AFFICHAGE TEMPLATE
    # --------------------------------------

    return render(

        request,

        'utilisateurs/inscription.html',

        {
            'form': form
        }
    )



# ==========================================
# CONNEXION UTILISATEUR
# ==========================================

@never_cache
def connexion_view(request):

    """
    Vue connexion utilisateur
    """

    # --------------------------------------
    # SI FORMULAIRE ENVOYE
    # --------------------------------------

    if request.method == 'POST':

        form = ConnexionForm(

            request.POST
        )

        # ----------------------------------
        # FORMULAIRE VALIDE
        # ----------------------------------

        if form.is_valid():

            username = form.cleaned_data['username']

            password = form.cleaned_data['password']

            # ----------------------------------
            # AUTHENTIFICATION DJANGO
            # ----------------------------------

            utilisateur = authenticate(

                request,

                username=username,

                password=password
            )

            # ----------------------------------
            # CONNEXION REUSSIE
            # ----------------------------------

            if utilisateur is not None:

                login(

                    request,

                    utilisateur
                )

                # ----------------------------------
                # SUPERUSER
                # ----------------------------------

                if utilisateur.is_superuser:

                    return redirect(

                        'dashboard_admin'
                    )

                # ----------------------------------
                # UTILISATEUR NORMAL
                # ----------------------------------

                return redirect(

                    'accueil'
                )

            # ----------------------------------
            # IDENTIFIANTS INCORRECTS
            # ----------------------------------

            else:

                form.add_error(

                    None,

                    "Nom utilisateur ou mot de passe incorrect."
                )

    # --------------------------------------
    # FORMULAIRE VIDE
    # --------------------------------------

    else:

        form = ConnexionForm()

    # --------------------------------------
    # AFFICHAGE TEMPLATE
    # --------------------------------------

    return render(

        request,

        'utilisateurs/connexion.html',

        {
            'form': form
        }
    )



# ==========================================
# DECONNEXION UTILISATEUR
# ==========================================

@never_cache
def deconnexion_view(request):

    """
    Déconnexion utilisateur
    """

    # Fermeture session
    logout(

        request
    )

    # Retour accueil
    return redirect(

        'accueil'
    )


# ==========================================
# PROFIL UTILISATEUR
# ==========================================

@login_required(login_url='connexion')
def profil_view(request):
    """
    Espace personnel : modifier les infos du profil.
    """

    if request.method == 'POST':
        form = ProfilForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil mis à jour avec succès.")
            return redirect('profil')
    else:
        form = ProfilForm(instance=request.user)

    return render(request, 'utilisateurs/profil.html', {'form': form})


# ==========================================
# CHANGEMENT DE MOT DE PASSE
# ==========================================

@login_required(login_url='connexion')
def changer_mot_de_passe_view(request):
    """
    Permet au citoyen connecté de changer son mot de passe.
    Met à jour la session pour éviter la déconnexion.
    """

    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Maintenir la session active après le changement
            update_session_auth_hash(request, user)
            messages.success(request, "Mot de passe modifié avec succès.")
            return redirect('profil')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'utilisateurs/changer_mot_de_passe.html', {'form': form})