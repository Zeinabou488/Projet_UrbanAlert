# ==========================================
# IMPORTATION FORMS DJANGO
# ==========================================

from django import forms


# ==========================================
# IMPORTATION FORMULAIRE DJANGO
# ==========================================

from django.contrib.auth.forms import UserCreationForm


# ==========================================
# IMPORTATION MODELE UTILISATEUR
# ==========================================

from .models import Utilisateur



# ==========================================
# FORMULAIRE INSCRIPTION
# ==========================================

class InscriptionForm(UserCreationForm):

    """
    Formulaire inscription utilisateur
    """

    # ======================================
    # EMAIL OBLIGATOIRE
    # ======================================

    email = forms.EmailField(

        required=True,

        label='Email'
    )

    # ======================================
    # TELEPHONE OBLIGATOIRE
    # ======================================

    telephone = forms.CharField(

        required=True,

        label='Téléphone'
    )

    # ======================================
    # PHOTO NON OBLIGATOIRE
    # ======================================

    photo_profil = forms.ImageField(

        required=False,

        label='Photo de profil'
    )

    # ======================================
    # CONFIGURATION FORMULAIRE
    # ======================================

    class Meta:

        # Modèle utilisé
        model = Utilisateur

        # Champs affichés
        fields = [

            'username',
            'email',
            'telephone',
            'photo_profil',
            'password1',
            'password2',
        ]

    # ======================================
    # PERSONNALISATION FORMULAIRE
    # ======================================

    def __init__(self, *args, **kwargs):

        """
        Personnalisation formulaire
        """

        super().__init__(*args, **kwargs)

        # ==================================
        # SUPPRESSION AIDES DJANGO
        # ==================================

        for field in self.fields.values():

            field.help_text = ''

        # ==================================
        # LABELS PROPRES
        # ==================================

        self.fields['username'].label = 'Nom utilisateur'

        self.fields['password1'].label = 'Mot de passe'

        self.fields['password2'].label = 'Confirmation mot de passe'

        # ==================================
        # PLACEHOLDERS
        # ==================================

        self.fields['username'].widget.attrs.update({

            'placeholder': 'Nom utilisateur',

            'class': 'form-input'
        })

        self.fields['email'].widget.attrs.update({

            'placeholder': 'Email',

            'class': 'form-input'
        })

        self.fields['telephone'].widget.attrs.update({

            'placeholder': 'Téléphone',

            'class': 'form-input'
        })

        self.fields['password1'].widget.attrs.update({

            'placeholder': 'Mot de passe',

            'class': 'form-input'
        })

        self.fields['password2'].widget.attrs.update({

            'placeholder': 'Confirmer mot de passe',

            'class': 'form-input'
        })

        # ==================================
        # INPUT FILE
        # ==================================

        self.fields['photo_profil'].widget.attrs.update({

            'class': 'file-input'
        })



# ==========================================
# FORMULAIRE CONNEXION
# ==========================================

class ConnexionForm(forms.Form):

    """
    Formulaire connexion utilisateur
    """

    # ======================================
    # USERNAME
    # ======================================

    username = forms.CharField(

        required=True,

        label='Nom utilisateur',

        max_length=150,

        widget=forms.TextInput(

            attrs={

                'placeholder': 'Nom utilisateur',

                'class': 'form-input'
            }
        )
    )

    # ======================================
    # PASSWORD
    # ======================================

    password = forms.CharField(

        required=True,

        label='Mot de passe',

        widget=forms.PasswordInput(

            attrs={

                'placeholder': 'Mot de passe',

                'class': 'form-input'
            }
        )
    )

    # ==========================================
# FORMULAIRE ADMIN MODIFICATION UTILISATEUR
# ==========================================

# ==========================================
# FORMULAIRE PROFIL (auto-modification)
# ==========================================

class ProfilForm(forms.ModelForm):
    """Formulaire de modification du profil par le citoyen lui-même."""

    class Meta:
        model = Utilisateur
        fields = ['username', 'email', 'telephone', 'photo_profil']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.help_text = ''
            if hasattr(field.widget, 'attrs'):
                field.widget.attrs['class'] = 'form-control'


# ==========================================
# FORMULAIRE ADMIN MODIFICATION UTILISATEUR
# ==========================================

class ModifierUtilisateurForm(forms.ModelForm):

    """
    Formulaire modification utilisateur
    """

    class Meta:

        # ----------------------------------
        # MODELE UTILISATEUR
        # ----------------------------------

        model = Utilisateur

        # ----------------------------------
        # CHAMPS MODIFIABLES
        # ----------------------------------

        fields = [

            'username',

            'email',

            'telephone',

            'photo_profil',

            'role',
        ]


    # ======================================
    # PERSONNALISATION FORMULAIRE
    # ======================================

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # ----------------------------------
        # PLACEHOLDERS
        # ----------------------------------

        self.fields['username'].widget.attrs.update({

            'placeholder': 'Nom utilisateur'
        })

        self.fields['email'].widget.attrs.update({

            'placeholder': 'Adresse email'
        })

        self.fields['telephone'].widget.attrs.update({

            'placeholder': 'Téléphone'
        })

        # ----------------------------------
        # SUPPRESSION HELP TEXT
        # ----------------------------------

        for field in self.fields.values():

            field.help_text = ''