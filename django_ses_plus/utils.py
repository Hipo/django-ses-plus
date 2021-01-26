import base64
from time import strftime

from django.core.mail import get_connection
from django.core.mail.message import EmailMultiAlternatives


def sent_email_upload_path(sent_email, filename):
    filename = filename.split(".")[0]
    return strftime("emails/%Y/%m/%d/%Y-%m-%d-%H-%M-%S-{}.html".format(filename))


def send_mail(subject, message, from_email, recipient_list, attachments=None, fail_silently=False, html_message=None):
    connection = get_connection(fail_silently=fail_silently)

    mail = EmailMultiAlternatives(subject, message, from_email, recipient_list, connection=connection)

    if html_message:
        mail.attach_alternative(html_message, 'text/html')

    if attachments:
        for attachment in attachments:
            mail.attach(attachment["name"], base64.b64decode(attachment["content"]), attachment["type"])

    return mail.send()
