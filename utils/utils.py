import datetime
import os
import smtplib
from collections import namedtuple
from email.message import EmailMessage
from pathlib import Path
from zipfile import ZipFile

import exceptions
import settings

LatSettings = namedtuple(
    'Latvia',
    [
        'source_dir',
        'handled_file_dir',
        'archive_dir',
        'ftp_dir',
        'ftp_group_id',
        'remote_dir'
    ]
)

BaseSettings = namedtuple(
    'BaseSettings',
    [
        'tmp_dir',
        'archive_dir',
        'test_dir',
        'log_dir',
        'email_server',
        'email_port',
        'email_login',
        'email_password',
        'email_recipients',
        'ssh_server',
        'ssh_user',
        'ssh_port'
    ]
)


def get_latvia_settings() -> LatSettings:
    try:
        latvia_settings = LatSettings(
            settings.LAT_SOURCE_DIR,
            settings.LAT_HANDLED_FILE_DIR,
            settings.LAT_ARCHIVE_DIR,
            settings.LAT_FTP_DIR,
            settings.LAT_FTP_GROUP_ID,
            settings.LAT_REMOTE_DIR)
    except AttributeError as err:
        raise exceptions.ConfigLoadError(err) from None
    return latvia_settings


def get_base_settings() -> BaseSettings:
    try:
        base_settings = BaseSettings(
            settings.TMP_DIR,
            settings.ARCHIVE_DIR,
            settings.TEST_DIR,
            settings.LOG_DIR,
            settings.EMAIL_SERVER,
            settings.EMAIL_PORT,
            settings.EMAIL_LOGIN,
            settings.EMAIL_PASSWORD,
            settings.EMAIL_RECIPIENTS,
            settings.SSH_SERVER,
            settings.SSH_USER,
            settings.SSH_PORT,
        )
    except AttributeError as err:
        raise exceptions.ConfigLoadError(err) from None
    return base_settings


def send_email(text: str, subject: str) -> None:
    """send email to recipient from settings.EMAIL_RECIPIENTS"""
    base_settings = get_base_settings()
    msg = EmailMessage()
    msg.set_content(text)
    msg['Subject'] = subject
    msg['From'] = 'mnp-parsing@lancktele.com'
    msg['To'] = base_settings.email_recipients

    server = smtplib.SMTP(
        host=base_settings.email_server,
        port=base_settings.email_port)
    server.starttls()
    server.login(
        user=base_settings.email_login,
        password=base_settings.email_password)
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
