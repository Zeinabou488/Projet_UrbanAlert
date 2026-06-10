from django.contrib import admin
from .models import ActionModeration


@admin.register(ActionModeration)
class ActionModerationAdmin(admin.ModelAdmin):
    list_display = ['signalement', 'admin', 'type_action', 'date_action']
    list_filter = ['type_action']
    readonly_fields = ['date_action']
