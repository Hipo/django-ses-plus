# Django SES Plus

Django module to store and send email with AWS SES. It's an extension for [django-ses](https://github.com/django-ses/django-ses) package.

## Releases

You can see the releases [here](https://github.com/Hipo/django-ses-plus/releases).

## Installation

1. pip install `django-ses-plus`. 

2. Add **django_ses_plus** to the `INSTALLED_APPS` in the settings file.

3. Configure settings.

```
DJANGO_SES_PLUS_SETTINGS = {
    "SEND_EMAIL": True,  # True by default.
    "CELERY_TASK_RETRY_KWARGS": {
        'max_retries': 15, 
        'countdown': 60
    }
}
```

4. `python manage.py migrate`

5. (Optional) Add `SendEmailMixin` to your auth user model.
```
from django_ses_plus.models import SendEmailMixin

class AuthUser(SendEmailMixin,...):
    ....
    
user.send_sms(subject, template_path, context, from_email=None, language=None)
# OR
from django_ses_plus.tasks import send_sms
send_email.delay(subject, to_email, html_message, from_email=None, message=None, recipient_id=None)
```

## Support

Please [open an issue](https://github.com/Hipo/django-ses-plus/issues/new) for support.

## Contributing

Please contribute using [Github Flow](https://guides.github.com/introduction/flow/). Create a branch, add commits, and [open a pull request](https://github.com/Hipo/django-ses-plus/compare/).
