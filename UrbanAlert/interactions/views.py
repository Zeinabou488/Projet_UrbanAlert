# ==========================================
# VUES : MODULE INTERACTIONS
# Votes citoyens et commentaires
# ==========================================

from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from signalements.models import Signalement
from .models import Vote, Commentaire


# ==========================================
# VUE : VOTER POUR UN SIGNALEMENT
# RG8 : un seul vote par citoyen par signalement
# ==========================================

@login_required(login_url='connexion')
@require_POST
def voter(request, signalement_id):
    """
    Ajoute ou retire le vote du citoyen connecté
    sur un signalement (toggle).
    Retourne JSON pour les requêtes AJAX.
    """

    signalement = get_object_or_404(Signalement, pk=signalement_id)

    # Vérifier si le citoyen a déjà voté (contrainte d'unicité RG8)
    vote_existant = Vote.objects.filter(
        utilisateur=request.user,
        signalement=signalement
    ).first()

    if vote_existant:
        # Toggle : retirer le vote si déjà voté
        vote_existant.delete()
        a_vote = False
        action = 'retire'
    else:
        # Créer le vote
        Vote.objects.create(
            utilisateur=request.user,
            signalement=signalement
        )
        a_vote = True
        action = 'ajoute'

    nb_votes = signalement.votes.count()

    # Réponse JSON si requête AJAX, sinon redirection
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'action': action,
            'nb_votes': nb_votes,
            'a_vote': a_vote,
        })

    return redirect('detail_signalement', pk=signalement_id)


# ==========================================
# VUE : AJOUTER UN COMMENTAIRE
# RG12 : uniquement pour les citoyens connectés
# ==========================================

@login_required(login_url='connexion')
@require_POST
def ajouter_commentaire(request, signalement_id):
    """
    Soumet un commentaire sur un signalement.
    Le contenu est validé côté serveur.
    """

    signalement = get_object_or_404(Signalement, pk=signalement_id)
    contenu = request.POST.get('contenu', '').strip()

    if contenu:
        Commentaire.objects.create(
            utilisateur=request.user,
            signalement=signalement,
            contenu=contenu
        )
        messages.success(request, "Votre commentaire a été ajouté.")
    else:
        messages.error(request, "Le commentaire ne peut pas être vide.")

    return redirect('detail_signalement', pk=signalement_id)


# ==========================================
# VUE : SUPPRIMER UN COMMENTAIRE (auteur)
# Le citoyen peut supprimer son propre commentaire
# ==========================================

@login_required(login_url='connexion')
def supprimer_commentaire(request, commentaire_id):
    """Supprime un commentaire appartenant à l'utilisateur connecté."""

    commentaire = get_object_or_404(
        Commentaire,
        pk=commentaire_id,
        utilisateur=request.user  # sécurité : seul l'auteur peut supprimer
    )
    signalement_id = commentaire.signalement_id
    commentaire.delete()
    messages.success(request, "Commentaire supprimé.")

    return redirect('detail_signalement', pk=signalement_id)
