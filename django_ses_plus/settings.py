from django.conf import settings

DJANGO_SES_PLUS_SETTINGS = getattr(settings, "DJANGO_SES_PLUS_SETTINGS", {})

DJANGO_SES_PLUS_SETTINGS.setdefault("SEND_EMAIL", True)
DJANGO_SES_PLUS_SETTINGS.setdefault("CELERY_TASK_RETRY_KWARGS", {'max_retries': 15, 'countdown': 60})
DJANGO_SES_PLUS_SETTINGS.setdefault("FILE_STORAGE_BACKEND", None)

# Get default from email from django settings.
DJANGO_SES_PLUS_SETTINGS.setdefault("DEFAULT_FROM_EMAIL", settings.DEFAULT_FROM_EMAIL)
