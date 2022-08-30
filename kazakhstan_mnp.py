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
from utils.loger_util import create_logger


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
        logger = create_logger(__name__, base_settings.log_dir)

        logger.info('start processing')
        ftp_files = retrieve_ftp_files(kz_settings)
        ftp_files.sort(key=lambda x: x[1]['modify'], reverse=True)
        ftp_file, modify_date = ftp_files[0]

        send_alarm(modify_date['modify'])

        logger.info(f'start load file {ftp_file}')
        try:
            zip_file = download_latest_file(ftp_file, base_settings, kz_settings)
        except Exception as err:
            logger.exception('error during load file via FTP\n\n{err}', exc_info=True, stack_info=True)
            raise exceptions.MnpProcessingError(err) from None
        logger.info('finished load')

        archive = shutil.copy(zip_file, kz_settings.archive_dir)
        if kz_settings.handled_file_path.exists():
            utils.archive_file(kz_settings.handled_file_path, kz_settings.archive_dir)

        with ZipFile(zip_file, 'r') as zip_f:
            attachment_files = zip_f.namelist()
            if not attachment_files or len(attachment_files) != 1:
                logger.warning(f'wrong zip attachment. Check archive {archive}')
                raise exceptions.BadSourceZipFile(
                    f'please check {zip_file} attachment')

            archive_name = attachment_files[0]
            tmp_file = Path(zip_f.extract(archive_name,
                                          base_settings.tmp_dir))
        try:
            logger.info('start parse file')
            parse_file(tmp_file, kz_settings)
        except exceptions.ParserError as err:
            logger.exception(f'an exception during parse file\n\n{err}', exc_info=True, stack_info=True)
            delete_temp_files(tmp_file, zip_file, kz_settings.lock_file)
            tb = traceback.format_exc()
            utils.send_email(text=f'{err}\n\n{tb})',
                             subject='Kazakhstan mnp parser error')

            return
        logger.info('finished parse file')
        shutil.move(kz_settings.lock_file, kz_settings.handled_file_path)
        delete_temp_files(zip_file, tmp_file)
        logger.info('finish processing')
    except Exception as err:
        logger.exception(f'an exception during processing\n\n{err}', exc_info=True, stack_info=True)
        delete_temp_files(tmp_file, zip_file, kz_settings.lock_file)
        raise exceptions.MnpProcessingError(
            f"an error during processing Kazakhstan mnp\n\n{err}") from None
