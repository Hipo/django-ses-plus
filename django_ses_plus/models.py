import base64
import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import models
from django.dispatch import receiver
from django.template.loader import render_to_string
from django.utils import translation
from django_ses import signals
from django.utils.translation import gettext_lazy as _

from django_ses_plus.settings import DJANGO_SES_PLUS_SETTINGS
from .utils import sent_email_upload_path, sent_email_attachment_upload_path


class SentEmail(models.Model):
    class Status(models.TextChoices):
        UNKNOWN = 'unknown', 'Unknown'
        SENT = 'sent', 'Sent'
        DELIVERED = 'delivered', 'Delivered'
        BOUNCED = 'bounced', 'Bounced'
        # Don't support rejects and rendering failures for now.
        # REJECTED = 'rejected', 'Rejected'
        # RENDERING_FAILURE = 'rendering-failure', 'Rendering Failure'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="sent_emails", on_delete=models.SET_NULL, null=True)
    to_email = models.EmailField()
    from_email = models.EmailField()
    subject = models.TextField()
    html = models.FileField(upload_to=sent_email_upload_path)

    # tracking & monitoring
    message_id = models.CharField(max_length=100, blank=True)
    status = models.CharField(choices=Status.choices, default=Status.UNKNOWN, max_length=50)
    bounce_type = models.CharField(max_length=50, blank=True)
    bounce_sub_type = models.CharField(max_length=50, blank=True)
    is_opened = models.BooleanField(default=False)
    is_clicked = models.BooleanField(default=False)
    is_complained = models.BooleanField(default=False)

    creation_datetime = models.DateTimeField(auto_now_add=True)
    update_datetime = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Sent Email')
        verbose_name_plural = _('Sent Emails')

    def __str__(self):
        return f"{self.subject} to {self.to_email}"

    @staticmethod
    @receiver(signals.send_received)
    def send_handler(sender, mail_obj, send_obj, **kwargs):
        message_id = mail_obj['messageId']
        SentEmail.objects.filter(
            message_id=message_id,
            status=SentEmail.Status.UNKNOWN,
        ).update(
            status=SentEmail.Status.SENT
        )

    @staticmethod
    @receiver(signals.delivery_received)
    def delivery_handler(sender, mail_obj, delivery_obj, **kwargs):
        message_id = mail_obj['messageId']
        recipients = delivery_obj['recipients']
        SentEmail.objects.filter(
            message_id=message_id,
            to_email__in=recipients,
        ).update(
            status=SentEmail.Status.DELIVERED
        )

    @staticmethod
    @receiver(signals.bounce_received)
    def bounce_handler(sender, mail_obj, bounce_obj, **kwargs):
        message_id = mail_obj['messageId']
        recipients = [r['emailAddress'] for r in bounce_obj['bouncedRecipients']]
        SentEmail.objects.filter(
            message_id=message_id,
            to_email__in=recipients,
        ).update(
            status=SentEmail.Status.BOUNCED,
            bounce_type=bounce_obj['bounceType'],
            bounce_sub_type=bounce_obj['bounceSubType'],
        )

    @staticmethod
    @receiver(signals.open_received)
    def open_handler(sender, mail_obj, open_obj, **kwargs):
        # open_obj does not provide recipient emails.
        message_id = mail_obj['messageId']
        SentEmail.objects.filter(
            message_id=message_id,
        ).update(
            status=SentEmail.Status.DELIVERED,
            is_opened=True
        )

    @staticmethod
    @receiver(signals.click_received)
    def click_handler(sender, mail_obj, click_obj, **kwargs):
        # click_obj does not provide recipient emails.
        message_id = mail_obj['messageId']
        SentEmail.objects.filter(
            message_id=message_id,
        ).update(
            status=SentEmail.Status.DELIVERED,
            is_clicked=True
        )

    @staticmethod
    @receiver(signals.complaint_received)
    def compliant_handler(sender, mail_obj, complaint_obj, **kwargs):
        message_id = mail_obj['messageId']
        recipients = complaint_obj['complainedRecipients']
        SentEmail.objects.filter(
            message_id=message_id,
            to_email__in=recipients,
        ).update(
            status=SentEmail.Status.DELIVERED,
            is_complained=True
        )


class SentEmailAttachment(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    sent_email = models.ForeignKey(to="django_ses_plus.SentEmail", related_name="attachments", on_delete=models.CASCADE)
    filename = models.CharField(max_length=255)
    content = models.FileField(upload_to=sent_email_attachment_upload_path)
    mimetype = models.CharField(help_text="e.g. text/html, application/pdf, image/png...", max_length=255)

    creation_datetime = models.DateTimeField(auto_now_add=True)
    update_datetime = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Sent Email Attachment")
        verbose_name_plural = _("Sent Email Attachments")

    def __str__(self):
        return f"{self.filename} ({self.mimetype})"


class SendEmailMixin(object):

    def get_to_email(self):
        return self.email

    def send_email(self, subject, template_path, context, from_email=None, language=None, attachments=None):
        from .tasks import send_email
        if not DJANGO_SES_PLUS_SETTINGS["SEND_EMAIL"]:
            return _("Email cannot be sent due to SEND_EMAIL flag in project settings.")

        if isinstance(self, get_user_model()):
            recipient_id = self.pk
        else:
            recipient_id = None

        if language:
            translation.activate(language)

        if attachments is not None:
            assert isinstance(attachments, list), "Attachments should be a `list` of `dict` objects."

            for attachment in attachments:
                assert all([key in attachment for key in ["filename", "content", "mimetype"]]), "Attachments should contain `filename`, `content` and `mimetype`."

                if isinstance(attachment["content"], bytes):
                    # Since celery only accepts JSON serializable types and `bytes` is not JSON serializable,
                    # Base64 encoding is used to be able to pass attachment content to the celery task,
                    attachment["content"] = base64.b64encode(attachment["content"]).decode("utf-8")
                else:
                    assert False, f"Attachment contents should be `bytes`, not {type(attachment['content'])}."

        html_message = render_to_string(template_path, context)
        send_email.delay(
            subject=subject,
            to_email=self.get_to_email(),
            html_message=html_message,
            attachments=attachments,
            from_email=from_email,
            recipient_id=recipient_id
        )

        if language:
            translation.deactivate()
