import datetime
import ftplib
from pathlib import Path
from typing import List, Dict, Tuple

import utils


def get_ftp_files(kzt_settings) -> List[Tuple[str, Dict[str, str]]]:
    print('statrt ftp')
    ftp = ftplib.FTP()
    ftp.connect(kzt_settings.ssh_server, kzt_settings.ssh_port)
    ftp.login(kzt_settings.ssh_login, kzt_settings.ssh_password)
    files = list(ftp.mlsd(facts=['modify']))
    ftp.close()
    return files


def download_latest_file(file_name, base_settings, kzt_settings: utils.KztSettings) -> Path:
    print(file_name)
    ftp = ftplib.FTP()
    ftp.connect(kzt_settings.ssh_server, kzt_settings.ssh_port)
    ftp.login(kzt_settings.ssh_login, kzt_settings.ssh_password)
    kzt_tmp = base_settings.tmp_dir.joinpath(file_name)
    with open(kzt_tmp, 'wb') as tmp_file:
        ftp.retrbinary(f'RETR {file_name}', tmp_file.write)
    ftp.close()
    return kzt_tmp


def send_alarm(modify_date: str):
    modify_date = datetime.datetime.strptime(modify_date, '%Y%m%d%H%M%S.%f')
    current_time = datetime.datetime.now()
    day_between = current_time - modify_date

    if day_between.days > 7:
        utils.send_email(text=f'last FTP modify was {day_between.days} days ago', subject='WARNING: Kazakhstan last update')


def file_handler(base_settings: utils.BaseSettings, kzt_settings: utils.KztSettings):
    files = get_ftp_files(kzt_settings)
    files.sort(key=lambda x: x[1]['modify'], reverse=True)
    file, modify_date = files[0]

    send_alarm(modify_date['modify'])
    tmp_file = download_latest_file(file, base_settings, kzt_settings)

