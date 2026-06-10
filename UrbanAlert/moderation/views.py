# ==========================================
# VUES : MODULE MODERATION
# Gestion des signalements par l'administrateur :
# changement de statut, suppression, journalisation
# ==========================================

from django.shortcuts import redirect, get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.http import require_POST

from signalements.models import Signalement, StatutSignalement, HistoriqueStatut
from interactions.models import Commentaire
from .models import ActionModeration


def admin_requis(view_func):
    """
    Décorateur personnalisé : vérifie que l'utilisateur est admin.
    Redirige vers l'accueil si ce n'est pas le cas.
    """
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_superuser:
            return redirect('accueil')
        return view_func(request, *args, **kwargs)
    return wrapper


# ==========================================
# VUE : CHANGER LE STATUT D'UN SIGNALEMENT
# Workflow : En attente -> En cours -> Résolu
# RG7 : réservé aux administrateurs
# ==========================================

@login_required(login_url='connexion')
@admin_requis
@require_POST
def changer_statut(request, signalement_id):
    """
    Change le statut d'un signalement.
    Enregistre l'historique du changement.
    """

    signalement = get_object_or_404(Signalement, pk=signalement_id)
    nouveau_statut_code = request.POST.get('statut')
    commentaire_admin = request.POST.get('commentaire_admin', '').strip()

    nouveau_statut = get_object_or_404(StatutSignalement, code=nouveau_statut_code)
    ancien_statut = signalement.statut

    # Enregistrer dans l'historique
    HistoriqueStatut.objects.create(
        signalement=signalement,
        ancien_statut=ancien_statut,
        nouveau_statut=nouveau_statut,
        admin=request.user,
        commentaire_admin=commentaire_admin or None
    )

    # Mettre à jour le statut courant
    signalement.statut = nouveau_statut

    # RG11 : renseigner la date de résolution si statut = Résolu
    if nouveau_statut_code == 'resolu':
        signalement.date_resolution = timezone.now()
    else:
        signalement.date_resolution = None

    signalement.save()

    messages.success(
        request,
        f"Statut mis à jour : {nouveau_statut.nom_statut}"
    )

    # Rediriger vers la page d'origine (dashboard ou détail)
    next_url = request.POST.get('next', '')
    if next_url:
        return redirect(next_url)
    return redirect('dashboard_signalements')


# ==========================================
# VUE : MODÉRER (supprimer/invalider) UN SIGNALEMENT
# Journalise l'action dans ACTION_MODERATION
# ==========================================

@login_required(login_url='connexion')
@admin_requis
def moderer_signalement(request, signalement_id):
    """
    Supprime ou invalide un signalement invalide.
    Enregistre l'action dans le journal de modération.
    """

    signalement = get_object_or_404(Signalement, pk=signalement_id)

    if request.method == 'POST':
        type_action = request.POST.get('type_action', 'suppression')
        motif = request.POST.get('motif', '').strip()

        # Journaliser l'action
        ActionModeration.objects.create(
            signalement=signalement,
            admin=request.user,
            type_action=type_action,
            motif=motif or None
        )

        if type_action == 'suppression':
            signalement.delete()
            messages.success(request, "Signalement supprimé.")
            return redirect('dashboard_signalements')
        elif type_action == 'rejet':
            statut_rejete = StatutSignalement.objects.filter(code='rejete').first()
            if statut_rejete:
                ancien_statut = signalement.statut
                HistoriqueStatut.objects.create(
                    signalement=signalement,
                    ancien_statut=ancien_statut,
                    nouveau_statut=statut_rejete,
                    admin=request.user,
                    commentaire_admin=motif or "Rejeté par modération"
                )
                signalement.statut = statut_rejete
                signalement.save()
            messages.warning(request, "Signalement rejeté.")
            return redirect('dashboard_signalements')

    context = {'signalement': signalement}
    return render(request, 'moderation/confirmer_moderation.html', context)


# ==========================================
# VUE : MODÉRER UN COMMENTAIRE
# ==========================================

@login_required(login_url='connexion')
@admin_requis
@require_POST
def moderer_commentaire(request, commentaire_id):
    """Masque un commentaire signalé comme inapproprié."""

    commentaire = get_object_or_404(Commentaire, pk=commentaire_id)
    commentaire.est_modere = True
    commentaire.save()
    messages.success(request, "Commentaire masqué.")

    return redirect('detail_signalement', pk=commentaire.signalement_id)
