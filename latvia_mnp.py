import csv
import os
import shutil
import traceback
from datetime import datetime
from pathlib import Path

import exceptions
import utils


def parse_file(file_in: Path,
               lat_settings: utils.LatSettings):
    """:return file_out: Path"""
    file_out: Path = lat_settings.lock_file
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


def file_handler(base_settings: utils.BaseSettings,
                 lat_settings: utils.LatSettings):
    if not lat_settings.source_file_path.exists():
        raise exceptions.SourceMnpFileNotExists(
            f'{lat_settings.source_file_path} does not exists')

    if not os.stat(lat_settings.source_file_path).st_size:
        raise exceptions.SourceMnpFileIsEmpty(
            f'{lat_settings.source_file_path} is empty')
    try:
        tmp_file = Path(shutil.copy(lat_settings.source_file_path,
                                    base_settings.tmp_dir))
        utils.archive_file(file_in=lat_settings.source_file_path,
                           archive_dir=lat_settings.archive_dir)
        if lat_settings.handled_file_path.exists():
            utils.archive_file(file_in=lat_settings.handled_file_path,
                               archive_dir=lat_settings.archive_dir)

        try:
            parse_file(tmp_file, lat_settings=lat_settings)
        except exceptions.ParserError as err:
            tb = traceback.format_exc()
            utils.send_email(text=f'{err}\n\n{tb})',
                             subject='Latvia mnp parser error')
            delete_temp_files(lat_settings, tmp_file)
            return

        shutil.move(lat_settings.lock_file, lat_settings.handled_file_path)
        utils.copy_to_smssw(file_in=lat_settings.handled_file_dir,
                            remoute_dir=lat_settings.remote_dir)

        delete_temp_files(lat_settings, tmp_file)
    except Exception as err:
        raise exceptions.MnpProcessingError(
            f"an error during processing Latvia's mnp\n\n{err}") from None


def delete_temp_files(lat_settings: utils.LatSettings, *args):
    for file in args:
        if file.exists():
            os.remove(file)
    if lat_settings.lock_file.exists():
        os.remove(lat_settings.lock_file)
    if lat_settings.source_file_path.exists():
        os.remove(lat_settings.source_file_path)


if __name__ == '__main__':
    b_settings = utils.get_base_settings()
    l_settings = utils.get_latvia_settings()
    file_handler(base_settings=b_settings,
                 lat_settings=l_settings)
