from django.db import models

class Signalement(models.Model):
    titre = models.CharField(max_length=200)
    description = models.TextField()
    localisation = models.CharField(max_length=255)
    date_creation = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(max_length=50, default='en attente')

    def __str__(self):
        return self.titre
# Create your models here.
