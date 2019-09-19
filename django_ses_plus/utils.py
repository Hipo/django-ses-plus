from time import strftime


def sent_email_upload_path(sent_email, filename):
    filename = filename.split(".")[0]
    return strftime("emails/%Y/%m/%d/%Y-%m-%d-%H-%M-%S-{}.html".format(filename))
