import csv
import os
import shutil
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple
from zipfile import ZipFile

import exceptions
import utils


def retrieve_ftp_files(kz_settings) -> List[Tuple[str, Dict[str, str]]]:
    kz_ftp = utils.SFTP(host=kz_settings.ssh_server,
                        port=kz_settings.ssh_port,
                        user=kz_settings.ssh_login,
                        passwd=kz_settings.ssh_password)
    with kz_ftp as sftp:
        files = list(sftp.mlsd(facts=['modify']))
    return files


def download_latest_file(file_name,
                         base_settings,
                         kz_settings: utils.KztSettings) -> Path:
    kz_tmp = base_settings.tmp_dir.joinpath(file_name)
    kz_ftp = utils.SFTP(host=kz_settings.ssh_server,
                        port=kz_settings.ssh_port,
                        user=kz_settings.ssh_login,
                        passwd=kz_settings.ssh_password)
    with kz_ftp as sftp:
        with open(kz_tmp, 'wb') as tmp_file:
            sftp.retrbinary(f'RETR {file_name}', tmp_file.write)
    return kz_tmp


def send_alarm(modify_date: str):
    modify_date = datetime.strptime(modify_date, '%Y%m%d%H%M%S.%f')
    current_time = datetime.now()
    day_between = current_time - modify_date

    if day_between.days > 7:
        utils.send_email(text=f'last FTP modify was '
                              f'{day_between.days} days ago',
                         subject='WARNING: Kazakhstan last update')


def parse_file(file_in: Path, kz_settings: utils.KztSettings) -> None:
    try:
        with open(file_in, 'r') as tmp_mnp, \
                open(kz_settings.lock_file, 'w') as lock_db:
            tmp_csv = csv.DictReader(tmp_mnp)
            db_csv = csv.writer(lock_db, delimiter=';')
            for row in tmp_csv:
                timestamp = int(
                    datetime.fromisoformat(
                        row['PortDate']).replace(
                        tzinfo=timezone.utc).timestamp())
                line = [row['Number'],
                        f"4010{row['MNC']}",
                        timestamp,
                        None,
                        row['OwnerId'], 1]
                db_csv.writerow(line)
    except Exception as err:
        raise exceptions.ParserError(
            f'an error during parse {file_in}\n\n{err}') from None


def delete_temp_files(*args):
    for file in args:
        if file.exists():
            os.remove(file)


def processing_mnp(base_settings: utils.BaseSettings,
                   kz_settings: utils.KztSettings):
    try:
        files = retrieve_ftp_files(kz_settings)
        files.sort(key=lambda x: x[1]['modify'], reverse=True)
        file, modify_date = files[0]

        send_alarm(modify_date['modify'])
        tmp_archive = download_latest_file(file, base_settings, kz_settings)
        shutil.copy(tmp_archive, kz_settings.archive_dir)

        with ZipFile(tmp_archive, 'r') as zip_file:
            archive_files = zip_file.namelist()
            if not archive_files or len(archive_files) != 1:
                raise exceptions.BadSourceZipFile(
                    f'please check {tmp_archive} attachment')

            archive_name = archive_files[0]
            try:
                tmp_file = Path(zip_file.extract(archive_name,
                                                 base_settings.tmp_dir))
                parse_file(tmp_file, kz_settings)
            except exceptions.ParserError as err:
                delete_temp_files(tmp_file, tmp_archive, kz_settings.lock_file)
                tb = traceback.format_exc()
                utils.send_email(text=f'{err}\n\n{tb})',
                                 subject='Kazakhstan mnp parser error')

                return

            shutil.move(kz_settings.lock_file, kz_settings.handled_file_path)
            delete_temp_files(tmp_archive, tmp_file)
    except Exception as err:
        delete_temp_files(tmp_file, tmp_archive, kz_settings.lock_file)
        raise exceptions.MnpProcessingError(
            f"an error during processing Kazakhstan mnp\n\n{err}") from None
