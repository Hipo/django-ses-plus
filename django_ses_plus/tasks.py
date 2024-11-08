import base64
from uuid import uuid4

from celery import shared_task

from django_ses_plus import logger
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from django.utils.translation import gettext_lazy as _

from .models import SentEmail, SentEmailAttachment
from .settings import DJANGO_SES_PLUS_SETTINGS
from .utils import send_mail


@shared_task(retry_kwargs=DJANGO_SES_PLUS_SETTINGS["CELERY_TASK_RETRY_KWARGS"])
def send_email(subject, to_email, html_message, from_email=None, message=None, recipient_id=None, attachments=None):
    if not DJANGO_SES_PLUS_SETTINGS["SEND_EMAIL"]:
        return _("Email cannot be sent due to SEND_EMAIL flag in project settings.")

    if not from_email:
        from_email = DJANGO_SES_PLUS_SETTINGS["DEFAULT_FROM_EMAIL"]

    num_sent, mail = send_mail(
        subject=subject,
        message=message,
        html_message=html_message,
        attachments=attachments,
        from_email=from_email,
        recipient_list=[to_email],
        fail_silently=False,
    )

    try:
        sent_email = SentEmail.objects.create(
            message_id=mail.extra_headers.get('message_id', ''),
            recipient_id=recipient_id,
            subject=subject,
            html=ContentFile(content=bytes(html_message, encoding="utf8"), name="{}.html".format(uuid4())),
            from_email=from_email,
            to_email=to_email,
        )
        if attachments:
            for attachment in attachments:
                SentEmailAttachment.objects.create(
                    sent_email=sent_email,
                    filename=attachment["filename"],
                    content=ContentFile(content=base64.b64decode(attachment["content"]), name=attachment["filename"]),
                    mimetype=attachment["mimetype"]
                )
    except Exception as e:
        # Do not retry if object creation fails.
        logger.error(str(e), exc_info=e, extra={'trace': True})
    else:
        return sent_email.id
