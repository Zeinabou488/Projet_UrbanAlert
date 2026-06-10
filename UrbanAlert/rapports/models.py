# ==========================================
# MODULE : RAPPORTS
# Gère la génération et l'archivage
# des rapports PDF (hebdomadaires / mensuels)
# ==========================================

from django.db import models
from django.conf import settings


# ==========================================
# TABLE RAPPORT_PDF
# Archive les rapports générés par les admins
# RG10 : associé à une période et un admin
# ==========================================

class RapportPDF(models.Model):

    # Type de rapport
    TYPE_CHOICES = [
        ('hebdomadaire', 'Hebdomadaire'),
        ('mensuel',      'Mensuel'),
    ]

    # Type : hebdomadaire ou mensuel
    type_rapport = models.CharField(
        max_length=15,
        choices=TYPE_CHOICES
    )

    # Début de la période couverte
    periode_debut = models.DateField()

    # Fin de la période couverte
    periode_fin = models.DateField()

    # Fichier PDF généré (stocké dans media/rapports/)
    fichier_pdf = models.FileField(
        upload_to='rapports/',
        null=True,
        blank=True
    )

    # Administrateur qui a généré le rapport
    genere_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='rapports_generes'
    )

    # Date de génération automatique
    date_generation = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Rapport PDF"
        verbose_name_plural = "Rapports PDF"
        ordering = ['-date_generation']

    def __str__(self):
        return (
            f"Rapport {self.get_type_rapport_display()} "
            f"du {self.periode_debut} au {self.periode_fin}"
        )
