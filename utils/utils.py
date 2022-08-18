import datetime
import os
import smtplib
from email.message import EmailMessage
from pathlib import Path
from zipfile import ZipFile

import exceptions
import settings


def check_settings():
    try:
        tmp_dir = settings.TMP_DIR
        archive_dir = settings.ARCHIVE_DIR
    except AttributeError as err:
        raise exceptions.CheckConfigError(err) from None
    for dir in (tmp_dir, archive_dir):
        if not dir.exists():
            try:
                os.makedirs(dir)
            except OSError as e:
                raise exceptions.CheckConfigError(e) from None


def send_email(text: str, subject: str) -> None:
    """send email to recipient from settings.EMAIL_RECIPIENTS"""
    msg = EmailMessage()
    msg.set_content(text)
    msg['Subject'] = subject
    msg['From'] = 'mnp-parsing@lancktele.com'
    msg['To'] = settings.EMAIL_RECIPIENTS

    server = smtplib.SMTP(
        host=settings.EMAIL_SERVER,
        port=settings.EMAIL_PORT)
    server.starttls()
    server.login(
        user=settings.EMAIL_LOGIN,
        password=settings.EMAIL_PASSWORD)
    server.send_message(msg)


def archive_file(file_in: Path, archive_dir: Path) -> Path:
    """copy file to archive_dir, gzip it and then delete"""
    file = os.path.basename(file_in)
    file_name, _ = os.path.splitext(file)
    archive_date = datetime.date.today().strftime('%d%m%Y')
    archive_file_name = f'{file_name}_{archive_date}.zip'
    archive_file_path = archive_dir.joinpath(archive_file_name)

    with ZipFile(archive_file_path, 'w') as archive_zip:
        archive_zip.write(file_in, arcname=file)
    os.remove(file_in)

    return archive_file_path


def push_file_to_server(file: Path) -> None:
    """copy file via ssh"""
    pass
