from uuid import uuid4

from celery import shared_task

from django_ses_plus import logger
from .settings import DJANGO_SES_PLUS_SETTINGS
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from django.utils.translation import ugettext_lazy as _

from .models import SentEmail


@shared_task(retry_kwargs=DJANGO_SES_PLUS_SETTINGS["CELERY_TASK_RETRY_KWARGS"])
def send_email(subject, to_email, html_message, from_email=None, message=None, recipient_id=None):
    if not DJANGO_SES_PLUS_SETTINGS["SEND_EMAIL"]:
        return _("Email cannot be sent due to SEND_EMAIL flag in project settings.")

    if not from_email:
        from_email = DJANGO_SES_PLUS_SETTINGS["DEFAULT_FROM_EMAIL"]

    send_mail(
        subject=subject,
        message=message,
        html_message=html_message,
        from_email=from_email,
        recipient_list=[to_email],
        fail_silently=False,
    )

    try:
        SentEmail.objects.create(
            recipient_id=recipient_id,
            subject=subject,
            html=ContentFile(content=bytes(html_message, encoding="utf8"), name="{}.html".format(uuid4())),
            from_email=from_email,
            to_email=to_email,
        )
    except Exception as e:
        # Do not retry if object creation fails.
        logger.error(str(e), exc_info=e, extra={'trace': True})
