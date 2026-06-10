# ==========================================
# FORMULAIRES : MODULE SIGNALEMENTS
# ==========================================

from django import forms
from localisation.models import Commune, Quartier
from .models import (
    CategorieProbleme,
    SousCategorie,
    Signalement,
    PhotoSignalement,
)


# ==========================================
# FORMULAIRE SOUMISSION SIGNALEMENT
# Accessible aux citoyens (connectés ou anonymes)
# ==========================================

class SignalementForm(forms.ModelForm):

    # Champ commune : non présent dans le modèle mais
    # utilisé pour filtrer les quartiers côté client
    commune = forms.ModelChoiceField(
        queryset=Commune.objects.all(),
        label="Commune",
        empty_label="-- Sélectionner une commune --",
        required=True
    )

    # Catégorie : filtre les sous-catégories côté client
    categorie = forms.ModelChoiceField(
        queryset=CategorieProbleme.objects.all(),
        label="Catégorie",
        empty_label="-- Sélectionner une catégorie --",
        required=True
    )

    # Photo principale (optionnelle)
    photo = forms.ImageField(
        required=False,
        label="Photo du problème (JPG ou PNG)",
        widget=forms.FileInput(attrs={'accept': 'image/jpeg,image/png'})
    )

    class Meta:
        model = Signalement
        fields = [
            'titre',
            'description',
            'priorite',
            'est_urgence',
            'est_anonyme',
            'sous_categorie',
            'quartier',
            'latitude',
            'longitude',
            'adresse_manuelle',
        ]
        widgets = {
            'titre': forms.TextInput(attrs={
                'placeholder': 'Titre court du problème',
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Décrivez le problème en détail...',
                'class': 'form-control',
                'rows': 4
            }),
            'priorite': forms.Select(attrs={'class': 'form-control'}),
            'sous_categorie': forms.Select(attrs={'class': 'form-control'}),
            'quartier': forms.Select(attrs={'class': 'form-control'}),
            'adresse_manuelle': forms.TextInput(attrs={
                'placeholder': 'Adresse ou repère (optionnel)',
                'class': 'form-control'
            }),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
            'est_urgence': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'est_anonyme': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'titre': 'Titre',
            'description': 'Description détaillée',
            'priorite': 'Niveau de priorité',
            'est_urgence': 'Situation d\'urgence (danger immédiat)',
            'est_anonyme': 'Soumettre anonymement',
            'sous_categorie': 'Sous-catégorie',
            'quartier': 'Quartier',
            'adresse_manuelle': 'Adresse ou repère',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Initialisation : aucune sous-catégorie et aucun quartier
        # Ils seront filtrés dynamiquement via JavaScript
        self.fields['sous_categorie'].queryset = SousCategorie.objects.none()
        self.fields['quartier'].queryset = Quartier.objects.none()

        # Si des données POST sont présentes (rechargement après erreur)
        if 'categorie' in self.data:
            try:
                cat_id = int(self.data.get('categorie'))
                self.fields['sous_categorie'].queryset = (
                    SousCategorie.objects.filter(categorie_id=cat_id)
                )
            except (ValueError, TypeError):
                pass

        if 'commune' in self.data:
            try:
                com_id = int(self.data.get('commune'))
                self.fields['quartier'].queryset = (
                    Quartier.objects.filter(commune_id=com_id)
                )
            except (ValueError, TypeError):
                pass

        # Ajout de la classe CSS commune
        for field_name, field in self.fields.items():
            if hasattr(field.widget, 'attrs'):
                if 'class' not in field.widget.attrs:
                    field.widget.attrs['class'] = 'form-control'


# ==========================================
# FORMULAIRE FILTRAGE SIGNALEMENTS (admin)
# ==========================================

class FiltreSignalementForm(forms.Form):

    commune = forms.ModelChoiceField(
        queryset=Commune.objects.all(),
        required=False,
        empty_label="Toutes les communes",
        label="Commune",
        widget=forms.Select(attrs={'class': 'form-control form-control-sm'})
    )

    categorie = forms.ModelChoiceField(
        queryset=CategorieProbleme.objects.all(),
        required=False,
        empty_label="Toutes les catégories",
        label="Catégorie",
        widget=forms.Select(attrs={'class': 'form-control form-control-sm'})
    )

    STATUT_CHOICES = [
        ('', 'Tous les statuts'),
        ('en_attente', 'En attente'),
        ('en_cours',   'En cours'),
        ('resolu',     'Résolu'),
        ('rejete',     'Rejeté'),
    ]

    statut = forms.ChoiceField(
        choices=STATUT_CHOICES,
        required=False,
        label="Statut",
        widget=forms.Select(attrs={'class': 'form-control form-control-sm'})
    )

    PRIORITE_CHOICES = [
        ('', 'Toutes les priorités'),
        ('faible', 'Faible'),
        ('moyen',  'Moyen'),
        ('urgent', 'Urgent'),
    ]

    priorite = forms.ChoiceField(
        choices=PRIORITE_CHOICES,
        required=False,
        label="Priorité",
        widget=forms.Select(attrs={'class': 'form-control form-control-sm'})
    )

    date_debut = forms.DateField(
        required=False,
        label="Du",
        widget=forms.DateInput(
            attrs={'type': 'date', 'class': 'form-control form-control-sm'}
        )
    )

    date_fin = forms.DateField(
        required=False,
        label="Au",
        widget=forms.DateInput(
            attrs={'type': 'date', 'class': 'form-control form-control-sm'}
        )
    )
