# ==========================================
# VUES : MODULE SIGNALEMENTS
# Soumission, liste, détail, mes signalements,
# carte interactive, API JSON pour filtres
# ==========================================

import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Q
from django.utils import timezone

from localisation.models import Commune, Quartier
from interactions.models import Vote
from .models import (
    CategorieProbleme,
    SousCategorie,
    Signalement,
    StatutSignalement,
    PhotoSignalement,
    HistoriqueStatut,
)
from .forms import SignalementForm, FiltreSignalementForm


# ==========================================
# VUE : SOUMISSION D'UN SIGNALEMENT
# Accessible aux citoyens connectés ET anonymes
# ==========================================

def soumettre_signalement(request):
    """
    Formulaire de soumission d'un nouveau signalement.
    - Citoyen connecté : auteur enregistré
    - Visiteur anonyme : est_anonyme = True
    """

    if request.method == 'POST':

        form = SignalementForm(request.POST, request.FILES)

        if form.is_valid():

            signalement = form.save(commit=False)

            # Associer l'utilisateur connecté s'il existe
            if request.user.is_authenticated:
                signalement.utilisateur = request.user
            else:
                # Forcer le flag anonyme si non connecté
                signalement.est_anonyme = True

            # Attribuer le statut initial "En attente"
            statut_initial = StatutSignalement.objects.filter(
                code='en_attente'
            ).first()
            signalement.statut = statut_initial

            signalement.save()

            # Enregistrer la première entrée d'historique
            HistoriqueStatut.objects.create(
                signalement=signalement,
                ancien_statut=None,
                nouveau_statut=statut_initial,
                commentaire_admin="Signalement créé"
            )

            # Sauvegarder la photo si fournie
            photo = request.FILES.get('photo')
            if photo:
                PhotoSignalement.objects.create(
                    signalement=signalement,
                    fichier=photo
                )

            messages.success(
                request,
                "Votre signalement a été soumis avec succès !"
            )
            return redirect('detail_signalement', pk=signalement.pk)

    else:
        form = SignalementForm()

    # Contexte enrichi pour la page
    context = {
        'form': form,
        'communes': Commune.objects.all(),
        'categories': CategorieProbleme.objects.prefetch_related('sous_categories').all(),
    }
    return render(request, 'signalements/soumettre.html', context)


# ==========================================
# VUE : LISTE DES SIGNALEMENTS (publique)
# Avec filtres par commune, catégorie, statut
# ==========================================

def liste_signalements(request):
    """
    Liste publique de tous les signalements avec filtres.
    Les signalements les plus votés remontent en priorité.
    """

    signalements = Signalement.objects.select_related(
        'sous_categorie__categorie',
        'quartier__commune',
        'statut',
        'utilisateur'
    ).annotate(
        nb_votes=Count('votes')
    ).order_by('-est_urgence', '-nb_votes', '-date_creation')

    form = FiltreSignalementForm(request.GET)

    if form.is_valid():
        # Filtre par commune
        commune = form.cleaned_data.get('commune')
        if commune:
            signalements = signalements.filter(quartier__commune=commune)

        # Filtre par catégorie
        categorie = form.cleaned_data.get('categorie')
        if categorie:
            signalements = signalements.filter(
                sous_categorie__categorie=categorie
            )

        # Filtre par statut
        statut = form.cleaned_data.get('statut')
        if statut:
            signalements = signalements.filter(statut__code=statut)

        # Filtre par priorité
        priorite = form.cleaned_data.get('priorite')
        if priorite:
            signalements = signalements.filter(priorite=priorite)

        # Filtre par date
        date_debut = form.cleaned_data.get('date_debut')
        if date_debut:
            signalements = signalements.filter(date_creation__date__gte=date_debut)

        date_fin = form.cleaned_data.get('date_fin')
        if date_fin:
            signalements = signalements.filter(date_creation__date__lte=date_fin)

    context = {
        'signalements': signalements,
        'form': form,
        'total': signalements.count(),
    }
    return render(request, 'signalements/liste.html', context)


# ==========================================
# VUE : DÉTAIL D'UN SIGNALEMENT
# Avec commentaires, votes, historique
# ==========================================

def detail_signalement(request, pk):
    """
    Page de détail d'un signalement.
    Affiche les photos, commentaires, votes et historique.
    """

    signalement = get_object_or_404(
        Signalement.objects.select_related(
            'sous_categorie__categorie',
            'quartier__commune',
            'statut',
            'utilisateur'
        ).annotate(nb_votes=Count('votes')),
        pk=pk
    )

    # Vérifier si l'utilisateur connecté a déjà voté
    a_vote = False
    if request.user.is_authenticated:
        a_vote = Vote.objects.filter(
            utilisateur=request.user,
            signalement=signalement
        ).exists()

    # Commentaires non modérés uniquement
    commentaires = signalement.commentaires.filter(
        est_modere=False
    ).select_related('utilisateur').order_by('date_commentaire')

    # Historique des statuts
    historique = signalement.historiques.select_related(
        'ancien_statut', 'nouveau_statut', 'admin'
    ).order_by('date_changement')

    # Photos
    photos = signalement.photos.all()

    context = {
        'signalement': signalement,
        'a_vote': a_vote,
        'commentaires': commentaires,
        'historique': historique,
        'photos': photos,
    }
    return render(request, 'signalements/detail.html', context)


# ==========================================
# VUE : MES SIGNALEMENTS (espace citoyen)
# Historique personnel des signalements soumis
# ==========================================

@login_required(login_url='connexion')
def mes_signalements(request):
    """
    Espace personnel : liste des signalements soumis
    par le citoyen connecté, avec statut et délai.
    """

    signalements = Signalement.objects.filter(
        utilisateur=request.user
    ).select_related(
        'sous_categorie__categorie',
        'quartier__commune',
        'statut'
    ).annotate(nb_votes=Count('votes')).order_by('-date_creation')

    context = {
        'signalements': signalements,
        'total': signalements.count(),
        'en_attente': signalements.filter(statut__code='en_attente').count(),
        'en_cours': signalements.filter(statut__code='en_cours').count(),
        'resolus': signalements.filter(statut__code='resolu').count(),
    }
    return render(request, 'signalements/mes_signalements.html', context)


# ==========================================
# VUE : CARTE INTERACTIVE
# Leaflet.js avec marqueurs colorés
# ==========================================

def carte_signalements(request):
    """
    Carte interactive Leaflet.js centrée sur Conakry.
    Les signalements sont chargés via l'API JSON.
    """

    communes = Commune.objects.all()
    categories = CategorieProbleme.objects.all()
    statuts = StatutSignalement.objects.all()

    context = {
        'communes': communes,
        'categories': categories,
        'statuts': statuts,
    }
    return render(request, 'signalements/carte.html', context)


# ==========================================
# API JSON : DONNÉES CARTE
# Retourne les signalements en GeoJSON simplifié
# ==========================================

def api_signalements_json(request):
    """
    Endpoint JSON pour alimenter la carte Leaflet.
    Supporte les filtres via paramètres GET.
    """

    signalements = Signalement.objects.select_related(
        'sous_categorie__categorie',
        'quartier__commune',
        'statut'
    ).annotate(nb_votes=Count('votes'))

    # Appliquer les filtres optionnels
    commune_id = request.GET.get('commune')
    if commune_id:
        signalements = signalements.filter(quartier__commune_id=commune_id)

    categorie_id = request.GET.get('categorie')
    if categorie_id:
        signalements = signalements.filter(sous_categorie__categorie_id=categorie_id)

    statut_code = request.GET.get('statut')
    if statut_code:
        signalements = signalements.filter(statut__code=statut_code)

    # Ne conserver que les signalements géolocalisés
    signalements = signalements.exclude(latitude=None).exclude(longitude=None)

    features = []
    for s in signalements:
        features.append({
            'id': s.id,
            'titre': s.titre,
            'description': s.description[:200],
            'priorite': s.priorite,
            'est_urgence': s.est_urgence,
            'categorie': s.sous_categorie.categorie.nom,
            'categorie_couleur': s.sous_categorie.categorie.couleur,
            'commune': s.quartier.commune.nom,
            'quartier': s.quartier.nom,
            'statut': s.statut.nom_statut,
            'statut_couleur': s.statut.couleur,
            'nb_votes': s.nb_votes,
            'date_creation': s.date_creation.strftime('%d/%m/%Y'),
            'lat': float(s.latitude),
            'lng': float(s.longitude),
            'url': f'/signalements/{s.id}/',
        })

    return JsonResponse({'signalements': features})


# ==========================================
# API JSON : SOUS-CATÉGORIES PAR CATÉGORIE
# Utilisé pour le formulaire dynamique
# ==========================================

def api_sous_categories(request, categorie_id):
    """Retourne les sous-catégories d'une catégorie."""
    sous_cats = SousCategorie.objects.filter(
        categorie_id=categorie_id
    ).values('id', 'nom')
    return JsonResponse({'sous_categories': list(sous_cats)})


# ==========================================
# API JSON : QUARTIERS PAR COMMUNE
# Utilisé pour le formulaire dynamique
# ==========================================

def api_quartiers(request, commune_id):
    """Retourne les quartiers d'une commune."""
    quartiers = Quartier.objects.filter(
        commune_id=commune_id
    ).values('id', 'nom')
    return JsonResponse({'quartiers': list(quartiers)})
