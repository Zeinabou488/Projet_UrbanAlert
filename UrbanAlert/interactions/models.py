# ==========================================
# MODULE : INTERACTIONS
# Gère les votes citoyens et les commentaires
# ==========================================

from django.db import models
from django.conf import settings
from signalements.models import Signalement


# ==========================================
# TABLE VOTE
# Un citoyen confirme un signalement par vote
# RG8 : une seule fois par signalement
# ==========================================

class Vote(models.Model):

    # Citoyen connecté ayant voté
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='votes'
    )

    # Signalement confirmé
    signalement = models.ForeignKey(
        Signalement,
        on_delete=models.CASCADE,
        related_name='votes'
    )

    # Date du vote
    date_vote = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Vote"
        verbose_name_plural = "Votes"
        # RG8 : contrainte d'unicité (un vote par citoyen par signalement)
        unique_together = ('utilisateur', 'signalement')

    def __str__(self):
        return (
            f"Vote de {self.utilisateur.username} "
            f"sur Signalement #{self.signalement_id}"
        )


# ==========================================
# TABLE COMMENTAIRE
# Les citoyens connectés commentent les signalements
# RG12 : rattaché à un utilisateur connecté
# ==========================================

class Commentaire(models.Model):

    # Auteur du commentaire (obligatoirement connecté)
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='commentaires'
    )

    # Signalement commenté
    signalement = models.ForeignKey(
        Signalement,
        on_delete=models.CASCADE,
        related_name='commentaires'
    )

    # Texte du commentaire
    contenu = models.TextField()

    # Date de publication
    date_commentaire = models.DateTimeField(auto_now_add=True)

    # True si commentaire masqué par modération
    est_modere = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Commentaire"
        verbose_name_plural = "Commentaires"
        ordering = ['date_commentaire']

    def __str__(self):
        return (
            f"Commentaire de {self.utilisateur.username} "
            f"sur Signalement #{self.signalement_id}"
        )
