# ==========================================
# MODULE : MODERATION
# Journalise toutes les actions administratives
# sur les signalements (validation, rejet, suppression)
# ==========================================

from django.db import models
from django.conf import settings
from signalements.models import Signalement


# ==========================================
# TABLE ACTION_MODERATION
# Traçabilité des actions admin (RG7)
# ==========================================

class ActionModeration(models.Model):

    # Types d'actions possibles
    TYPE_ACTION_CHOICES = [
        ('validation',   'Validation'),
        ('rejet',        'Rejet'),
        ('suppression',  'Suppression'),
        ('restauration', 'Restauration'),
        ('invalidation', 'Invalidation'),
    ]

    # Signalement concerné par l'action
    signalement = models.ForeignKey(
        Signalement,
        on_delete=models.CASCADE,
        related_name='actions_moderation'
    )

    # Administrateur responsable de l'action
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='actions_moderation'
    )

    # Type d'action effectuée
    type_action = models.CharField(
        max_length=20,
        choices=TYPE_ACTION_CHOICES
    )

    # Motif de l'action (ex: "contenu inapproprié")
    motif = models.TextField(blank=True, null=True)

    # Date de l'action
    date_action = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Action de modération"
        verbose_name_plural = "Actions de modération"
        ordering = ['-date_action']

    def __str__(self):
        return (
            f"{self.get_type_action_display()} "
            f"sur Signalement #{self.signalement_id} "
            f"par {self.admin}"
        )
