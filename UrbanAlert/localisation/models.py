# ==========================================
# MODULE : LOCALISATION
# Gère les communes et quartiers de Conakry
# ==========================================

from django.db import models


# ==========================
# TABLE COMMUNE
# Référentiel des 5 communes de Conakry
# ==========================

class Commune(models.Model):

    # Nom de la commune (ex: Kaloum, Ratoma...)
    nom = models.CharField(
        max_length=100,
        unique=True
    )

    # Description optionnelle de la commune
    description = models.TextField(
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = "Commune"
        verbose_name_plural = "Communes"
        ordering = ['nom']

    def __str__(self):
        return self.nom


# ==========================
# TABLE QUARTIER
# Chaque quartier appartient à une commune
# ==========================

class Quartier(models.Model):

    # Commune d'appartenance (relation N,1)
    commune = models.ForeignKey(
        Commune,
        on_delete=models.CASCADE,
        related_name='quartiers'
    )

    # Nom du quartier
    nom = models.CharField(
        max_length=100
    )

    class Meta:
        verbose_name = "Quartier"
        verbose_name_plural = "Quartiers"
        ordering = ['commune__nom', 'nom']
        # Un quartier doit être unique dans sa commune
        unique_together = ('commune', 'nom')

    def __str__(self):
        return f"{self.nom} ({self.commune.nom})"
