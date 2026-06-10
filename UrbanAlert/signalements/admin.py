# ==========================================
# ADMIN : MODULE SIGNALEMENTS
# ==========================================

from django.contrib import admin
from .models import (
    CategorieProbleme,
    SousCategorie,
    StatutSignalement,
    Signalement,
    PhotoSignalement,
    HistoriqueStatut
)


# Affichage des sous-catégories dans la page catégorie
class SousCategorieInline(admin.TabularInline):
    model = SousCategorie
    extra = 2


# Affichage des photos dans la page signalement
class PhotoInline(admin.TabularInline):
    model = PhotoSignalement
    extra = 0
    readonly_fields = ['date_upload']


# Affichage de l'historique dans la page signalement
class HistoriqueInline(admin.TabularInline):
    model = HistoriqueStatut
    extra = 0
    readonly_fields = ['date_changement']


@admin.register(CategorieProbleme)
class CategorieProblemeAdmin(admin.ModelAdmin):
    list_display = ['nom', 'couleur', 'icone']
    search_fields = ['nom']
    inlines = [SousCategorieInline]


@admin.register(SousCategorie)
class SousCategorieAdmin(admin.ModelAdmin):
    list_display = ['nom', 'categorie']
    list_filter = ['categorie']
    search_fields = ['nom', 'categorie__nom']


@admin.register(StatutSignalement)
class StatutSignalementAdmin(admin.ModelAdmin):
    list_display = ['nom_statut', 'code', 'ordre', 'couleur']
    ordering = ['ordre']


@admin.register(Signalement)
class SignalementAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'titre', 'priorite', 'est_urgence',
        'statut', 'date_creation', 'est_anonyme'
    ]
    list_filter = [
        'statut', 'priorite', 'est_urgence',
        'est_anonyme', 'sous_categorie__categorie',
        'quartier__commune'
    ]
    search_fields = ['titre', 'description']
    readonly_fields = ['date_creation', 'date_resolution']
    inlines = [PhotoInline, HistoriqueInline]


@admin.register(PhotoSignalement)
class PhotoSignalementAdmin(admin.ModelAdmin):
    list_display = ['id', 'signalement', 'date_upload']
    readonly_fields = ['date_upload']


@admin.register(HistoriqueStatut)
class HistoriqueStatutAdmin(admin.ModelAdmin):
    list_display = ['signalement', 'ancien_statut', 'nouveau_statut', 'admin', 'date_changement']
    readonly_fields = ['date_changement']
