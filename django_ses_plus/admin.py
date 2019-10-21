from django.contrib import admin

from .models import SentEmail


class SentEmailAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Details", {"fields": ("id", "subject", "from_email", "to_email", "creation_datetime",)}),
        ("Content", {"fields": ("html",)}),
    )
    readonly_fields = ("id", "subject", "from_email", "to_email", "creation_datetime", "html")
    list_display = ("id", "to_email", "subject", "creation_datetime")
    search_fields = ("to_email", "subject", )

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


admin.site.register(SentEmail, SentEmailAdmin)
