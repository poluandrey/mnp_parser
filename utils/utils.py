import os
import smtplib
from datetime import datetime
from email.message import EmailMessage
from ftplib import FTP
from pathlib import Path
from typing import List, NamedTuple, Optional
from zipfile import ZipFile

from paramiko import AutoAddPolicy, SSHClient

import exceptions
import settings


class SFTP(FTP):

    def __init__(self,
                 host,
                 port,
                 user: Optional[str] = None,
                 passwd: Optional[str] = None):
        super(SFTP, self).__init__()
        if host and port:
            self.connect(host, port)
            if user:
                self.login(user, passwd)


class LatSettings(NamedTuple):
    source_dir: Path
    source_file_name: str
    source_file_path: Path
    handled_file_dir: Path
    handled_file_name: str
    handled_file_path: Path
    lock_file: Path
    archive_dir: Path
    ftp_dir: Path
    ftp_group_id: int


class KztSettings(NamedTuple):
    handled_file_dir: Path
    handled_file_name: str
    handled_file_path: Path
    lock_file: Path
    archive_dir: Path
    ssh_server: str
    ssh_port: int
    ssh_login: str
    ssh_password: str
    ftp_dir: Path
    ftp_group_id: int


class BelSettings(NamedTuple):
    source_dir: Path
    source_file_mask: str
    handled_file_dir: Path
    handled_file_name: str
    handled_file_path: Path
    lock_file: Path
    archive_dir: Path
    ftp_dir: Path
    ftp_group_id: int


class BaseSettings(NamedTuple):
    tmp_dir: Path
    archive_dir: Path
    file_storage: Path
    log_dir: Path
    sync_dir: Path
    remote_sync_dir: Path
    source_sync_dir: Path
    hlr_proxy_file: str
    hlr_resale_file: str
    email_server: str
    email_port: int
    email_login: str
    email_password: str
    email_recipients: List
    ssh_server: str
    ssh_user: str
    ssh_port: int
    lat_conf: LatSettings
    kz_conf: KztSettings
    bel_conf: BelSettings


def get_latvia_settings() -> LatSettings:
    try:
        latvia_settings = LatSettings(
            settings.LAT_SOURCE_DIR,
            settings.LAT_SOURCE_FILE_NAME,
            settings.LAT_SOURCE_DIR.joinpath(
                settings.LAT_SOURCE_FILE_NAME),
            settings.LAT_HANDLED_FILE_DIR,
            settings.LAT_HANDLED_FILE_NAME,
            settings.LAT_HANDLED_FILE_DIR.joinpath(
                settings.LAT_HANDLED_FILE_NAME),
            settings.LAT_HANDLED_FILE_DIR.joinpath(
                f'{settings.LAT_HANDLED_FILE_NAME}.lock'),
            settings.LAT_ARCHIVE_DIR,
            settings.LAT_FTP_DIR,
            settings.LAT_FTP_GROUP_ID)
    except AttributeError as err:
        raise exceptions.ConfigLoadError(err) from None
    return latvia_settings


def get_kazakhstan_settings() -> KztSettings:
    try:
        kazakhstan_settings = KztSettings(
            settings.KZT_HANDLED_FILE_DIR,
            settings.KZT_HANDLED_FILE_NAME,
            settings.KZT_HANDLED_FILE_DIR.joinpath(
                settings.KZT_HANDLED_FILE_NAME),
            settings.KZT_HANDLED_FILE_DIR.joinpath(
                f'{settings.KZT_HANDLED_FILE_NAME}.lock'),
            settings.KZT_ARCHIVE_DIR,
            settings.KZT_SSH_SERVER,
            settings.KZT_SSH_PORT,
            settings.KZT_SSH_USER,
            settings.KZT_SSH_PASSWD,
            settings.KZT_FTP_DIR,
            settings.KZT_FTP_GROUP_ID
        )
    except AttributeError as err:
        raise exceptions.ConfigLoadError(err) from None
    return kazakhstan_settings


def get_belarus_settings() -> BelSettings:
    try:
        belarus_settings = BelSettings(
            settings.BEL_SOURCE_DIR,
            str(settings.BEL_SOURCE_DIR.joinpath(
                settings.BEL_SOURCE_FILE_MASK)),
            settings.BEL_HANDLED_FILE_DIR,
            settings.BEL_HANDLED_FILE_NAME,
            settings.BEL_HANDLED_FILE_DIR.joinpath(
                settings.BEL_HANDLED_FILE_NAME),
            settings.BEL_HANDLED_FILE_DIR.joinpath(
                f'{settings.BEL_HANDLED_FILE_NAME}.lock'),
            settings.BEL_ARCHIVE_DIR,
            settings.BEL_FTP_DIR,
            settings.BEL_FTP_GROUP_ID
        )
    except AttributeError as err:
        raise exceptions.ConfigLoadError(err) from None
    return belarus_settings


def get_base_settings() -> BaseSettings:
    try:
        base_settings = BaseSettings(
            settings.TMP_DIR,
            settings.ARCHIVE_DIR,
            settings.FILE_STORAGE,
            settings.LOG_DIR,
            settings.SYNC_DIR,
            settings.REMOTE_SYNC_DIR,
            settings.SOURCE_RESALE_DIR,
            settings.HLR_PROXY_FILE,
            settings.HLR_RESALE_FILE,
            settings.EMAIL_SERVER,
            settings.EMAIL_PORT,
            settings.EMAIL_LOGIN,
            settings.EMAIL_PASSWORD,
            settings.EMAIL_RECIPIENTS,
            settings.SSH_SERVER,
            settings.SSH_USER,
            settings.SSH_PORT,
            get_latvia_settings(),
            get_kazakhstan_settings(),
            get_belarus_settings()
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
    """copy file to archive_dir and gzip it"""
    file = os.path.basename(file_in)
    file_name, _ = os.path.splitext(file)
    archive_date = datetime.now().strftime('%d%m%Y_%H%M%S')
    archive_file_name = f'{file_name}-{archive_date}.zip'
    archive_file_path = archive_dir.joinpath(archive_file_name)

    with ZipFile(archive_file_path, 'w') as archive_zip:
        archive_zip.write(file_in, arcname=file)
    return archive_file_path


def copy_to_smssw(file_in: str,
                  remote_dir: str,
                  base_settings: BaseSettings) -> None:
    """copy file via ssh to smssw"""
    ssh = SSHClient()
    ssh.set_missing_host_key_policy(AutoAddPolicy())

    ssh.connect(base_settings.ssh_server,
                base_settings.ssh_port,
                base_settings.ssh_user)
    with ssh.open_sftp() as sftp:
        sftp.put(file_in, remote_dir)

    ssh.close()


def copy_to_ftp_folder():
    """copy to FTP folder and change user/group ownership"""
    pass


def show_config(d: NamedTuple, indent=0):
    for key, value in d._asdict().items():
        if isinstance(value, LatSettings) or isinstance(value, KztSettings) or isinstance(value, BelSettings):
            print('-' * 60)
            print(f'{key}')
            show_config(value, indent + 4)
        else:
            print(' ' * indent + f'{key}: ' + str(value))
