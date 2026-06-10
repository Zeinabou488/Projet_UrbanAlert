# ==========================================
# VUES : MODULE RAPPORTS
# Statistiques, graphiques et génération PDF
# ==========================================

import io
from datetime import date, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, FileResponse
from django.db.models import Count, Avg, F, ExpressionWrapper, DurationField
from django.db.models.functions import TruncMonth
from django.contrib import messages

from signalements.models import Signalement, CategorieProbleme, StatutSignalement
from localisation.models import Commune
from .models import RapportPDF
from .pdf_generator import generer_pdf_rapport


def admin_requis(view_func):
    """Décorateur : accès réservé aux administrateurs."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return redirect('accueil')
        return view_func(request, *args, **kwargs)
    return wrapper


# ==========================================
# VUE : TABLEAU DE STATISTIQUES
# Accessible aux administrateurs
# ==========================================

@login_required(login_url='connexion')
@admin_requis
def statistiques(request):
    """
    Page de statistiques complètes :
    - Signalements par catégorie et commune
    - Taux de résolution
    - Délai moyen
    - Top 10 plus votés
    - Évolution mensuelle
    """

    # --- Signalements par catégorie ---
    par_categorie = (
        CategorieProbleme.objects
        .annotate(nb=Count('sous_categories__signalements'))
        .order_by('-nb')
    )

    # --- Signalements par commune ---
    par_commune = (
        Commune.objects
        .annotate(nb=Count('quartiers__signalements'))
        .order_by('-nb')
    )

    # --- Taux de résolution global ---
    total = Signalement.objects.count()
    resolus = Signalement.objects.filter(statut__code='resolu').count()
    taux_resolution = round((resolus / total * 100) if total > 0 else 0, 1)

    # --- Taux de résolution par commune ---
    taux_par_commune = []
    for commune in Commune.objects.all():
        nb_total = Signalement.objects.filter(quartier__commune=commune).count()
        nb_resolus = Signalement.objects.filter(
            quartier__commune=commune,
            statut__code='resolu'
        ).count()
        taux = round((nb_resolus / nb_total * 100) if nb_total > 0 else 0, 1)
        taux_par_commune.append({
            'commune': commune.nom,
            'total': nb_total,
            'resolus': nb_resolus,
            'taux': taux,
        })

    # --- Top 10 signalements les plus votés ---
    top_votes = (
        Signalement.objects
        .annotate(nb_votes=Count('votes'))
        .order_by('-nb_votes')[:10]
    )

    # --- Évolution mensuelle sur 12 mois ---
    evolution_mensuelle = (
        Signalement.objects
        .annotate(mois=TruncMonth('date_creation'))
        .values('mois')
        .annotate(nb=Count('id'))
        .order_by('mois')
    )

    # Préparer les données pour Chart.js (JSON-friendly)
    labels_mois = [str(e['mois'].strftime('%b %Y')) for e in evolution_mensuelle if e['mois']]
    data_mois = [e['nb'] for e in evolution_mensuelle]

    labels_cat = [c.nom for c in par_categorie]
    data_cat = [c.nb for c in par_categorie]

    labels_com = [c.nom for c in par_commune]
    data_com = [c.nb for c in par_commune]

    context = {
        'par_categorie': par_categorie,
        'par_commune': par_commune,
        'taux_resolution': taux_resolution,
        'taux_par_commune': taux_par_commune,
        'top_votes': top_votes,
        'evolution_mensuelle': evolution_mensuelle,
        'total': total,
        'resolus': resolus,
        'en_attente': Signalement.objects.filter(statut__code='en_attente').count(),
        'en_cours': Signalement.objects.filter(statut__code='en_cours').count(),
        # JSON pour Chart.js
        'labels_mois': labels_mois,
        'data_mois': data_mois,
        'labels_cat': labels_cat,
        'data_cat': data_cat,
        'labels_com': labels_com,
        'data_com': data_com,
    }

    return render(request, 'rapports/statistiques.html', context)


# ==========================================
# VUE : LISTE DES RAPPORTS GÉNÉRÉS
# ==========================================

@login_required(login_url='connexion')
@admin_requis
def liste_rapports(request):
    """Affiche l'historique des rapports PDF générés."""

    rapports = RapportPDF.objects.select_related('genere_par').order_by('-date_generation')
    return render(request, 'rapports/liste_rapports.html', {'rapports': rapports})


# ==========================================
# VUE : GÉNÉRER UN RAPPORT PDF
# Hebdomadaire ou mensuel, avec ReportLab
# ==========================================

@login_required(login_url='connexion')
@admin_requis
def generer_rapport(request):
    """
    Génère un rapport PDF et l'archive dans la base.
    Type : hebdomadaire (7 derniers jours) ou mensuel (30 jours).
    """

    if request.method == 'POST':
        type_rapport = request.POST.get('type_rapport', 'hebdomadaire')

        # Calculer la période couverte
        aujourd_hui = date.today()
        if type_rapport == 'hebdomadaire':
            debut = aujourd_hui - timedelta(days=7)
        else:
            debut = aujourd_hui - timedelta(days=30)

        fin = aujourd_hui

        # Générer le contenu PDF
        pdf_content = generer_pdf_rapport(type_rapport, debut, fin)

        # Sauvegarder le rapport en base
        rapport = RapportPDF(
            type_rapport=type_rapport,
            periode_debut=debut,
            periode_fin=fin,
            genere_par=request.user
        )

        # Sauvegarder le fichier PDF dans media/rapports/
        from django.core.files.base import ContentFile
        nom_fichier = f"rapport_{type_rapport}_{debut}_{fin}.pdf"
        rapport.fichier_pdf.save(nom_fichier, ContentFile(pdf_content))
        rapport.save()

        messages.success(request, f"Rapport {type_rapport} généré avec succès.")

        # Proposer le téléchargement immédiat
        return HttpResponse(
            pdf_content,
            content_type='application/pdf',
            headers={
                'Content-Disposition': f'attachment; filename="{nom_fichier}"'
            }
        )

    return render(request, 'rapports/generer_rapport.html')


# ==========================================
# VUE : TÉLÉCHARGER UN RAPPORT ARCHIVÉ
# ==========================================

@login_required(login_url='connexion')
@admin_requis
def telecharger_rapport(request, rapport_id):
    """Télécharge un rapport PDF déjà archivé."""

    rapport = get_object_or_404(RapportPDF, pk=rapport_id)

    if rapport.fichier_pdf:
        return FileResponse(
            rapport.fichier_pdf.open('rb'),
            content_type='application/pdf',
            as_attachment=True,
            filename=f"rapport_{rapport.type_rapport}_{rapport.periode_debut}.pdf"
        )

    messages.error(request, "Fichier PDF introuvable.")
    return redirect('liste_rapports')
