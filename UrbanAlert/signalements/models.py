# ==========================================
# MODULE : SIGNALEMENTS
# Entité centrale du système UrbanAlert
# Gère les catégories, sous-catégories,
# statuts, signalements, photos et historique
# ==========================================

from django.db import models
from django.conf import settings
from localisation.models import Quartier


# ==========================================
# TABLE CATEGORIE_PROBLEME
# Les 9 grandes familles de problèmes urbains
# ==========================================

class CategorieProbleme(models.Model):

    # Nom de la catégorie (ex: Voirie, Eau...)
    nom = models.CharField(max_length=100, unique=True)

    # Description détaillée
    description = models.TextField(blank=True, null=True)

    # Couleur hexadécimale pour la carte Leaflet
    # ex: #e74c3c pour rouge
    couleur = models.CharField(
        max_length=7,
        default='#2ecc71',
        help_text="Couleur hexadécimale ex: #e74c3c"
    )

    # Icône FontAwesome pour l'affichage
    # ex: fa-road, fa-tint, fa-bolt
    icone = models.CharField(
        max_length=50,
        default='fa-exclamation-circle'
    )

    class Meta:
        verbose_name = "Catégorie de problème"
        verbose_name_plural = "Catégories de problèmes"
        ordering = ['nom']

    def __str__(self):
        return self.nom


# ==========================================
# TABLE SOUS_CATEGORIE
# Précise la nature exacte du problème
# ==========================================

class SousCategorie(models.Model):

    # Catégorie mère (relation N,1)
    categorie = models.ForeignKey(
        CategorieProbleme,
        on_delete=models.CASCADE,
        related_name='sous_categories'
    )

    # Nom de la sous-catégorie
    nom = models.CharField(max_length=100)

    # Description optionnelle
    description = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Sous-catégorie"
        verbose_name_plural = "Sous-catégories"
        ordering = ['categorie__nom', 'nom']
        unique_together = ('categorie', 'nom')

    def __str__(self):
        return f"{self.categorie.nom} > {self.nom}"


# ==========================================
# TABLE STATUT_SIGNALEMENT
# Référentiel du workflow : En attente -> Résolu
# ==========================================

class StatutSignalement(models.Model):

    # Valeurs possibles des statuts
    STATUTS = [
        ('en_attente', 'En attente'),
        ('en_cours',   'En cours'),
        ('resolu',     'Résolu'),
        ('rejete',     'Rejeté'),
    ]

    # Code unique du statut (slug)
    code = models.CharField(
        max_length=20,
        unique=True,
        choices=STATUTS
    )

    # Libellé lisible
    nom_statut = models.CharField(max_length=50)

    # Ordre logique dans le workflow
    ordre = models.PositiveSmallIntegerField(default=0)

    # Couleur d'affichage pour les badges
    couleur = models.CharField(
        max_length=20,
        default='secondary',
        help_text="Classe CSS de couleur (primary, success, danger...)"
    )

    class Meta:
        verbose_name = "Statut de signalement"
        verbose_name_plural = "Statuts de signalement"
        ordering = ['ordre']

    def __str__(self):
        return self.nom_statut


# ==========================================
# TABLE SIGNALEMENT
# Entité centrale : problème urbain soumis
# ==========================================

class Signalement(models.Model):

    # --- Niveaux de priorité ---
    PRIORITE_CHOICES = [
        ('faible', 'Faible'),
        ('moyen',  'Moyen'),
        ('urgent', 'Urgent'),
    ]

    # Titre court du problème
    titre = models.CharField(max_length=200)

    # Description détaillée
    description = models.TextField()

    # Niveau de priorité : Faible / Moyen / Urgent
    priorite = models.CharField(
        max_length=10,
        choices=PRIORITE_CHOICES,
        default='moyen'
    )

    # Bouton urgence : danger immédiat
    est_urgence = models.BooleanField(default=False)

    # True si soumis sans compte (citoyen anonyme)
    est_anonyme = models.BooleanField(default=False)

    # Auteur connecté (nullable pour les anonymes)
    utilisateur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='signalements'
    )

    # Nature du problème (sous-catégorie)
    sous_categorie = models.ForeignKey(
        SousCategorie,
        on_delete=models.PROTECT,
        related_name='signalements'
    )

    # Localisation administrative (quartier)
    quartier = models.ForeignKey(
        Quartier,
        on_delete=models.PROTECT,
        related_name='signalements'
    )

    # Coordonnées GPS optionnelles
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )

    # Adresse saisie manuellement en complément
    adresse_manuelle = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    # Statut courant du signalement
    statut = models.ForeignKey(
        StatutSignalement,
        on_delete=models.PROTECT,
        related_name='signalements'
    )

    # Date de création automatique
    date_creation = models.DateTimeField(auto_now_add=True)

    # Date de résolution (renseignée quand statut = Résolu)
    date_resolution = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Signalement"
        verbose_name_plural = "Signalements"
        ordering = ['-date_creation']
        indexes = [
            # Index pour les filtres fréquents du dashboard
            models.Index(fields=['statut', 'date_creation']),
            models.Index(fields=['quartier']),
        ]

    def __str__(self):
        return f"[{self.id}] {self.titre}"

    def nombre_votes(self):
        """Retourne le nombre de votes confirmant ce signalement."""
        return self.votes.count()

    def delai_traitement_jours(self):
        """Calcule le délai de traitement en jours si résolu."""
        if self.date_resolution:
            delta = self.date_resolution - self.date_creation
            return delta.days
        return None

    def get_commune(self):
        """Retourne la commune du signalement."""
        return self.quartier.commune


# ==========================================
# TABLE PHOTO_SIGNALEMENT
# Images jointes à un signalement (JPG/PNG)
# ==========================================

class PhotoSignalement(models.Model):

    # Signalement auquel appartient la photo
    signalement = models.ForeignKey(
        Signalement,
        on_delete=models.CASCADE,
        related_name='photos'
    )

    # Fichier image (stocké dans media/signalements/)
    fichier = models.ImageField(
        upload_to='signalements/',
        help_text="Format JPG ou PNG uniquement"
    )

    # Date d'ajout automatique
    date_upload = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Photo de signalement"
        verbose_name_plural = "Photos de signalement"

    def __str__(self):
        return f"Photo #{self.id} - Signalement #{self.signalement_id}"


# ==========================================
# TABLE HISTORIQUE_STATUT
# Trace chaque changement de statut
# Assure la traçabilité complète (RG6, RG7, RG11)
# ==========================================

class HistoriqueStatut(models.Model):

    # Signalement concerné
    signalement = models.ForeignKey(
        Signalement,
        on_delete=models.CASCADE,
        related_name='historiques'
    )

    # Ancien statut (null si c'est le premier enregistrement)
    ancien_statut = models.ForeignKey(
        StatutSignalement,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='+'
    )

    # Nouveau statut appliqué
    nouveau_statut = models.ForeignKey(
        StatutSignalement,
        on_delete=models.PROTECT,
        related_name='+'
    )

    # Administrateur responsable du changement
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='historiques_statuts'
    )

    # Date du changement
    date_changement = models.DateTimeField(auto_now_add=True)

    # Note de traitement optionnelle
    commentaire_admin = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Historique de statut"
        verbose_name_plural = "Historiques de statuts"
        ordering = ['-date_changement']

    def __str__(self):
        return (
            f"Signalement #{self.signalement_id} : "
            f"{self.ancien_statut} -> {self.nouveau_statut}"
        )
