import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.template.loader import render_to_string
from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from django_ses_plus.settings import DJANGO_SES_PLUS_SETTINGS
from .utils import sent_email_upload_path


class SentEmail(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="sent_emails", on_delete=models.SET_NULL, null=True)
    to_email = models.EmailField()
    from_email = models.EmailField()
    subject = models.TextField()
    html = models.FileField(upload_to=sent_email_upload_path)

    creation_datetime = models.DateTimeField(auto_now_add=True)
    update_datetime = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Sent Email')
        verbose_name_plural = _('Sent Emails')

    def __str__(self):
        return f"{self.subject} to {self.to_email}"


class SendEmailMixin(object):

    def get_to_email(self):
        return self.email

    def send_email(self, subject, template_path, context, from_email=None, language=None):
        from .tasks import send_email
        if not DJANGO_SES_PLUS_SETTINGS["SEND_EMAIL"]:
            return _("Email cannot be sent due to SEND_EMAIL flag in project settings.")

        if isinstance(self, get_user_model()):
            recipient_id = self.pk
        else:
            recipient_id = None

        if language:
            translation.activate(language)

        html_message = render_to_string(template_path, context)
        send_email.delay(
            subject=subject,
            to_email=self.get_to_email(),
            html_message=html_message,
            from_email=from_email,
            recipient_id=recipient_id
        )

        if language:
            translation.deactivate()
