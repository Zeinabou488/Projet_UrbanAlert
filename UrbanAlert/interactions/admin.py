from django.contrib import admin
from .models import Vote, Commentaire


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['utilisateur', 'signalement', 'date_vote']
    readonly_fields = ['date_vote']


@admin.register(Commentaire)
class CommentaireAdmin(admin.ModelAdmin):
    list_display = ['utilisateur', 'signalement', 'date_commentaire', 'est_modere']
    list_filter = ['est_modere']
    readonly_fields = ['date_commentaire']
    actions = ['moderer_commentaires']

    def moderer_commentaires(self, request, queryset):
        queryset.update(est_modere=True)
    moderer_commentaires.short_description = "Modérer les commentaires sélectionnés"
