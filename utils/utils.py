import os
import shutil
import smtplib
from email.message import EmailMessage
from pathlib import Path

import exceptions
import settings


def check_settings():
    tmp_dir = settings.TMP_DIR
    if not tmp_dir.exists():
        try:
            os.makedirs(tmp_dir)
        except OSError as e:
            raise exceptions.CheckConfigError(e) from None
    archive_dir = settings.ARCHIVE_DIR
    if not archive_dir.exists():
        try:
            os.makedirs(archive_dir)
        except OSError as e:
            raise exceptions.CheckConfigError(e).with_traceback() from None


def send_email(text: str, subject: str) -> None:
    """send email to recipient from settings.EMAIL_RECIPIENTS"""
    msg = EmailMessage()
    msg.set_content(text)
    msg['Subject'] = subject
    msg['From'] = 'mnp-parsing@lancktele.com'
    msg['To'] = settings.EMAIL_RECIPIENTS

    server = smtplib.SMTP(host=settings.EMAIL_SERVER, port=settings.EMAIL_PORT)
    server.starttls()
    server.login(user=settings.EMAIL_LOGIN, password=settings.EMAIL_PASSWORD)
    server.send_message(msg)


def archive_file(file: Path, archive_dir: Path) -> None:
    """copy file to archive_dir, gzip it and then delete"""




def push_file_to_server(file: Path) -> None:
    """copy file via ssh"""
    pass
