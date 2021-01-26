import base64
from os import path
from time import strftime
from uuid import uuid4

from django.core.mail import get_connection
from django.core.mail.message import EmailMultiAlternatives


def sent_email_upload_path(sent_email, filename):
    filename = filename.split(".")[0]
    return strftime("emails/%Y/%m/%d/%Y-%m-%d-%H-%M-%S-{}.html".format(filename))


def sent_email_attachment_upload_path(sent_email_attachment, filename):
    extension = path.splitext(filename)[1]
    return strftime(f"email-attachments/%Y/%m/%d/{uuid4().hex}{extension}")


def send_mail(subject, message, from_email, recipient_list, fail_silently=False, html_message=None, attachments=None):
    connection = get_connection(fail_silently=fail_silently)

    mail = EmailMultiAlternatives(subject, message, from_email, recipient_list, connection=connection)

    if html_message:
        mail.attach_alternative(html_message, 'text/html')

    if attachments:
        for attachment in attachments:
            mail.attach(attachment["filename"], base64.b64decode(attachment["content"]), attachment["mimetype"])

    num_sent = mail.send()
    return num_sent, mail
