from django.contrib import admin, messages
from django.core.exceptions import ValidationError

from django_ses_plus.settings import DJANGO_SES_PLUS_SETTINGS
from django_ses_plus.tasks import send_email
from .models import SentEmail


def resend_email(modeladmin, request, queryset):
    if queryset.count() > 1:
        raise ValidationError("You should resend email one by one.")

    for sent_email in queryset:
        html_message = sent_email.html.read().decode("utf-8")

        send_email(
            subject=sent_email.subject,
            to_email=sent_email.to_email,
            from_email=sent_email.from_email,
            html_message=html_message
        )

        messages.info(request, f'Email to f{sent_email.to_email} is re-sent.')

resend_email.short_description = "Resend email"


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

        if DJANGO_SES_PLUS_SETTINGS["CAN_RESEND_FROM_ADMIN_PANEL"]:
            actions += [resend_email]

        return actions

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


admin.site.register(SentEmail, SentEmailAdmin)
