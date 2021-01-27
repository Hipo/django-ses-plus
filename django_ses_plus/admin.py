from django.contrib import admin

from .models import SentEmail


class SentEmailAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Details", {"fields": ("id", "subject", "from_email", "to_email", "creation_datetime",)}),
        ("Content", {"fields": ("html",)}),
        ("Monitoring", {"fields": ("message_id", "status", "bounce_type", "bounce_sub_type", "is_opened", "is_clicked", "is_complained")}),
    )
    readonly_fields = ("id", "subject", "from_email", "to_email", "creation_datetime", "html", "message_id", "status", "bounce_type", "bounce_sub_type", "is_opened", "is_clicked", "is_complained")
    list_display = ("id", "to_email", "subject", "status", "creation_datetime")
    list_filter = ("status", "is_opened", "is_clicked", "is_complained")
    search_fields = ("to_email", "subject", )
    date_hierarchy = "creation_datetime"

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
