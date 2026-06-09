# ==========================================
# ADMIN : MODULE LOCALISATION
# ==========================================

from django.contrib import admin
from .models import Commune, Quartier


# Affichage des quartiers directement dans la page Commune
class QuartierInline(admin.TabularInline):
    model = Quartier
    extra = 3


@admin.register(Commune)
class CommuneAdmin(admin.ModelAdmin):
    list_display = ['nom', 'description']
    search_fields = ['nom']
    inlines = [QuartierInline]


@admin.register(Quartier)
class QuartierAdmin(admin.ModelAdmin):
    list_display = ['nom', 'commune']
    list_filter = ['commune']
    search_fields = ['nom', 'commune__nom']
