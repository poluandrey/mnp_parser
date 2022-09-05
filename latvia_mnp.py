import csv
import os
import shutil
import traceback
from datetime import datetime
from pathlib import Path

import exceptions
import utils
from utils.loger_util import create_logger


def parse_file(file_in: Path,
               base_settings: utils.BaseSettings):
    """:return file_out: Path"""
    file_out: Path = base_settings.lat_conf.lock_file
    rn2mcc: dict = {'BC2': '247002', 'BC4': '247005',
                    'BC1': '247001', 'BC3': '247003', }
    rn_key = rn2mcc.keys()
    operator2mcc: dict = {'Tele2': '247002', 'BITE Latvija': '247005',
                          'Latvijas Mobilais Telefons': '247001',
                          'Telekom Baltija': '247003'}

    with open(file_in, 'r') as f_in, open(file_out, 'w') as f_out:
        in_csv = csv.reader(f_in, delimiter=';')
        out_csv = csv.writer(f_out, delimiter=';')

        for row in in_csv:
            if not row or not all(row):
                raise exceptions.LatviaParserError(
                    f'empty row or cell found!!\n\n{row}')
            try:
                rn: str = row[3].strip()[0:3]
                if rn in rn_key and rn.startswith('BC'):
                    mccmnc: str = rn2mcc[rn]
                    msisdn: str = f'371{row[2].strip()}'
                    port_date: int = int(
                        datetime.strptime(row[4],
                                          ' %Y.%m.%d %H:%M:%S').timestamp())
                    out_csv.writerow([msisdn, mccmnc, port_date])
                elif rn.startswith('BC') and rn not in rn_key:
                    mccmnc: str = operator2mcc[row[1].strip()]
                    msisdn: str = f'371{row[2].strip()}'
                    port_date: int = int(datetime.strptime(
                        row[4],
                        ' %Y.%m.%d %H:%M:%S').timestamp())
                    out_csv.writerow([msisdn, mccmnc, port_date])
            except Exception as err:
                raise exceptions.LatviaParserError(
                    f'error in row {row} \n {err})') from None


def file_handler(base_settings: utils.BaseSettings):
    logger = create_logger(__name__)
    logger.info('start processing')
    if not base_settings.lat_conf.source_file_path.exists():
        msg = f'{base_settings.lat_conf.source_file_path} not exists'
        logger.warning(msg)
        utils.send_email(text=msg,
                         subject='Latvia mnp parser error')
        return

    if not os.stat(base_settings.lat_conf.source_file_path).st_size:
        msg = f'{base_settings.lat_conf.source_file_path} is empty'
        logger.warning(msg)
        utils.send_email(text=msg,
                         subject='Latvia mnp parser error')
        return
    try:
        tmp_file = Path(shutil.copy(base_settings.lat_conf.source_file_path,
                                    base_settings.tmp_dir))
        utils.archive_file(file_in=base_settings.lat_conf.source_file_path,
                           archive_dir=base_settings.lat_conf.archive_dir)
        if base_settings.lat_conf.handled_file_path.exists():
            utils.archive_file(file_in=base_settings.lat_conf.handled_file_path,
                               archive_dir=base_settings.lat_conf.archive_dir)

        try:
            logger.info('start parse file')
            parse_file(tmp_file, base_settings)
            logger.info('finished parse file')
        except exceptions.ParserError as err:
            logger.exception(f'an exception during parse file\n\n{err}',
                             exc_info=True, stack_info=True)
            tb = traceback.format_exc()
            utils.send_email(text=f'an exception during parse '
                                  f'file\n\n{err}\n\n{tb})',
                             subject='Latvia mnp parser error')
            delete_temp_files(base_settings, tmp_file)
            return

        shutil.move(base_settings.lat_conf.lock_file, base_settings.lat_conf.handled_file_path)

        delete_temp_files(base_settings, tmp_file)
        logger.info('finished processing')
    except Exception as err:
        logger.exception(f'an error during processing \n\n{err}',
                         exc_info=True, stack_info=True)
        delete_temp_files(base_settings, tmp_file)
        raise exceptions.MnpProcessingError(
            f"an error during processing Latvia's mnp\n\n{err}") from None


def delete_temp_files(base_settings: utils.BaseSettings, *args):
    for file in args:
        if file.exists():
            os.remove(file)
    if base_settings.lat_conf.lock_file.exists():
        os.remove(base_settings.lat_conf.lock_file)
    if base_settings.lat_conf.source_file_path.exists():
        os.remove(base_settings.lat_conf.source_file_path)
