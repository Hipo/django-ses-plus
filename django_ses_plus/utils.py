from time import strftime

from django.template.loader import render_to_string
from django.utils import translation
from django.utils.translation import ugettext_lazy as _

from django_ses_plus.settings import DJANGO_SES_PLUS_SETTINGS


def sent_email_upload_path(sent_email, filename):
    filename = filename.split(".")[0]
    return strftime("emails/%Y/%m/%d/%Y-%m-%d-%H-%M-%S-{}.html".format(filename))
