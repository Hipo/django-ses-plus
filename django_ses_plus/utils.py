from time import strftime

from django.utils.module_loading import import_string

from .settings import DJANGO_SES_PLUS_SETTINGS


def sent_email_upload_path(sent_email, filename):
    filename = filename.split(".")[0]
    return strftime("emails/%Y/%m/%d/%Y-%m-%d-%H-%M-%S-{}.html".format(filename))


def get_file_storage_backend():
    if DJANGO_SES_PLUS_SETTINGS["FILE_STORAGE_BACKEND"]:
        return import_string(DJANGO_SES_PLUS_SETTINGS["FILE_STORAGE_BACKEND"])()
