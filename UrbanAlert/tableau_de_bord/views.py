# ==========================================
# VUES : TABLEAU DE BORD ADMINISTRATEUR
# Vue d'ensemble, gestion des signalements,
# gestion des utilisateurs
# ==========================================

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone

from utilisateurs.models import Utilisateur
from utilisateurs.forms import ModifierUtilisateurForm
from signalements.models import Signalement, StatutSignalement, CategorieProbleme
from signalements.forms import FiltreSignalementForm
from localisation.models import Commune
from moderation.models import ActionModeration


def admin_requis(view_func):
    """Décorateur : réserve l'accès aux administrateurs."""
    @login_required(login_url='connexion')
    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser:
            return redirect('accueil')
        return view_func(request, *args, **kwargs)
    return wrapper


# ==========================================
# VUE : DASHBOARD PRINCIPAL
# Vue d'ensemble en temps réel
# ==========================================

@admin_requis
def dashboard_admin(request):
    """
    Tableau de bord principal :
    - Statistiques du jour et globales
    - Signalements urgents récents
    - Répartition par commune et statut
    """

    aujourd_hui = timezone.now().date()

    # Statistiques globales
    total_signalements = Signalement.objects.count()
    signalements_jour = Signalement.objects.filter(
        date_creation__date=aujourd_hui
    ).count()
    en_attente = Signalement.objects.filter(statut__code='en_attente').count()
    en_cours = Signalement.objects.filter(statut__code='en_cours').count()
    resolus = Signalement.objects.filter(statut__code='resolu').count()
    urgences = Signalement.objects.filter(est_urgence=True).exclude(
        statut__code='resolu'
    ).count()

    taux_resolution = round(
        (resolus / total_signalements * 100) if total_signalements > 0 else 0, 1
    )

    # Signalements urgents non résolus (priorité dashboard)
    signalements_urgents = Signalement.objects.filter(
        est_urgence=True
    ).exclude(statut__code='resolu').select_related(
        'sous_categorie__categorie', 'quartier__commune', 'statut'
    ).annotate(nb_votes=Count('votes')).order_by('-date_creation')[:5]

    # 10 derniers signalements
    derniers_signalements = Signalement.objects.select_related(
        'sous_categorie__categorie', 'quartier__commune', 'statut', 'utilisateur'
    ).annotate(nb_votes=Count('votes')).order_by('-date_creation')[:10]

    # Répartition par commune
    par_commune = Commune.objects.annotate(
        nb=Count('quartiers__signalements')
    ).order_by('-nb')

    # Utilisateurs actifs
    total_utilisateurs = Utilisateur.objects.filter(is_active=True).count()

    context = {
        'utilisateur': request.user,
        'total_signalements': total_signalements,
        'signalements_jour': signalements_jour,
        'en_attente': en_attente,
        'en_cours': en_cours,
        'resolus': resolus,
        'urgences': urgences,
        'taux_resolution': taux_resolution,
        'signalements_urgents': signalements_urgents,
        'derniers_signalements': derniers_signalements,
        'par_commune': par_commune,
        'total_utilisateurs': total_utilisateurs,
        'total_admins': Utilisateur.objects.filter(is_superuser=True).count(),
    }

    return render(request, 'tableau_de_bord/dashboard.html', context)


# ==========================================
# VUE : LISTE DES SIGNALEMENTS (admin)
# Filtres complets + actions de statut
# ==========================================

@admin_requis
def dashboard_signalements(request):
    """
    Liste complète des signalements avec filtres avancés.
    L'admin peut changer les statuts directement.
    """

    signalements = Signalement.objects.select_related(
        'sous_categorie__categorie',
        'quartier__commune',
        'statut',
        'utilisateur'
    ).annotate(nb_votes=Count('votes')).order_by(
        '-est_urgence', '-date_creation'
    )

    form = FiltreSignalementForm(request.GET)

    if form.is_valid():
        commune = form.cleaned_data.get('commune')
        if commune:
            signalements = signalements.filter(quartier__commune=commune)

        categorie = form.cleaned_data.get('categorie')
        if categorie:
            signalements = signalements.filter(sous_categorie__categorie=categorie)

        statut = form.cleaned_data.get('statut')
        if statut:
            signalements = signalements.filter(statut__code=statut)

        priorite = form.cleaned_data.get('priorite')
        if priorite:
            signalements = signalements.filter(priorite=priorite)

        date_debut = form.cleaned_data.get('date_debut')
        if date_debut:
            signalements = signalements.filter(date_creation__date__gte=date_debut)

        date_fin = form.cleaned_data.get('date_fin')
        if date_fin:
            signalements = signalements.filter(date_creation__date__lte=date_fin)

    statuts = StatutSignalement.objects.all()

    context = {
        'signalements': signalements,
        'form': form,
        'total': signalements.count(),
        'statuts': statuts,
    }

    return render(request, 'tableau_de_bord/signalements.html', context)


# ==========================================
# VUE : DÉTAIL SIGNALEMENT (admin)
# Avec panneau de gestion complet
# ==========================================

@admin_requis
def detail_signalement_admin(request, pk):
    """Vue admin du détail d'un signalement avec actions."""

    signalement = get_object_or_404(
        Signalement.objects.select_related(
            'sous_categorie__categorie',
            'quartier__commune',
            'statut',
            'utilisateur'
        ).annotate(nb_votes=Count('votes')),
        pk=pk
    )

    statuts = StatutSignalement.objects.all()
    historique = signalement.historiques.select_related(
        'ancien_statut', 'nouveau_statut', 'admin'
    ).order_by('date_changement')
    photos = signalement.photos.all()
    commentaires = signalement.commentaires.select_related('utilisateur')

    context = {
        'signalement': signalement,
        'statuts': statuts,
        'historique': historique,
        'photos': photos,
        'commentaires': commentaires,
    }
    return render(request, 'tableau_de_bord/detail_signalement.html', context)


# ==========================================
# VUE : LISTE DES UTILISATEURS
# ==========================================

@admin_requis
def liste_utilisateurs(request):
    """Liste et gestion des comptes utilisateurs."""

    utilisateurs = Utilisateur.objects.all().order_by('-id')

    context = {'utilisateurs': utilisateurs}
    return render(request, 'tableau_de_bord/utilisateurs.html', context)


# ==========================================
# VUE : DÉSACTIVER UN UTILISATEUR
# ==========================================

@admin_requis
def supprimer_utilisateur(request, user_id):
    """Désactive le compte d'un utilisateur (soft delete)."""

    try:
        utilisateur = Utilisateur.objects.get(id=user_id)
    except Utilisateur.DoesNotExist:
        return redirect('liste_utilisateurs')

    # Un admin ne peut pas se désactiver lui-même
    if utilisateur == request.user:
        messages.error(request, "Vous ne pouvez pas désactiver votre propre compte.")
        return redirect('liste_utilisateurs')

    if request.method == 'POST':
        utilisateur.is_active = False
        utilisateur.save()
        messages.success(request, f"Compte de {utilisateur.username} désactivé.")
        return redirect('liste_utilisateurs')

    return render(
        request,
        'tableau_de_bord/confirmer_suppression.html',
        {'utilisateur': utilisateur}
    )


# ==========================================
# VUE : RÉACTIVER UN UTILISATEUR
# ==========================================

@admin_requis
def reactiver_utilisateur(request, user_id):
    """Réactive un compte utilisateur désactivé."""

    try:
        utilisateur = Utilisateur.objects.get(id=user_id)
    except Utilisateur.DoesNotExist:
        return redirect('liste_utilisateurs')

    utilisateur.is_active = True
    utilisateur.save()
    messages.success(request, f"Compte de {utilisateur.username} réactivé.")
    return redirect('liste_utilisateurs')


# ==========================================
# VUE : MODIFIER UN UTILISATEUR
# ==========================================

@admin_requis
def modifier_utilisateur(request, user_id):
    """Modification des informations d'un utilisateur par l'admin."""

    try:
        utilisateur = Utilisateur.objects.get(id=user_id)
    except Utilisateur.DoesNotExist:
        return redirect('liste_utilisateurs')

    if request.method == 'POST':
        form = ModifierUtilisateurForm(
            request.POST, request.FILES, instance=utilisateur
        )
        if form.is_valid():
            form.save()
            messages.success(request, "Utilisateur modifié avec succès.")
            return redirect('liste_utilisateurs')
    else:
        form = ModifierUtilisateurForm(instance=utilisateur)

    return render(
        request,
        'tableau_de_bord/modifier_utilisateur.html',
        {'form': form, 'utilisateur': utilisateur}
    )
