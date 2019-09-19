from time import strftime

from django.template.loader import render_to_string
from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from django_ses_plus.settings import DJANGO_SES_PLUS_SETTINGS


def sent_email_upload_path(sent_email, filename):
    filename = filename.split(".")[0]
    return strftime("emails/%Y/%m/%d/%Y-%m-%d-%H-%M-%S-{}.html".format(filename))


def send_email_with_template(subject, to_email, template_path, context, language=None, from_email=None):
    if not DJANGO_SES_PLUS_SETTINGS["SEND_EMAIL"]:
        return _("Email cannot be sent due to SEND_EMAIL flag in project settings.")

    from .tasks import send_email

    # Send email in given language.
    if language:
        translation.activate(language)

    html_message = render_to_string(template_path, context)
    send_email.delay(subject=subject, to_email=to_email, html_message=html_message, from_email=from_email)

    if language:
        translation.deactivate()
