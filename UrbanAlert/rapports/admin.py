from django.contrib import admin
from .models import RapportPDF


@admin.register(RapportPDF)
class RapportPDFAdmin(admin.ModelAdmin):
    list_display = ['type_rapport', 'periode_debut', 'periode_fin', 'genere_par', 'date_generation']
    list_filter = ['type_rapport']
    readonly_fields = ['date_generation']
