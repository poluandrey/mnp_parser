import csv
import os
import shutil
from pathlib import Path
from typing import List
from zipfile import ZipFile

import exceptions
import utils
from utils.loger_util import create_logger


def define_load_mode(files: List) -> str:
    """
    get extension from list of file and define load mode
    for Port_All_* and Number_plan* return FULL
    for *Incremental* return Incremental
    """
    port_all = filter(
        lambda n: n.startswith('Port_All') or n.startswith('Numbering_plan'),
        files)
    port_inc = filter(
        lambda n: n.startswith('Port_Increment') or n.startswith('Return_Increment'),
        files)
    if any(port_all):
        return 'full'
    elif any(port_inc):
        return 'incremental'
    return 'undefined'


def sync(handled_files: List[Path],
         sync_type: str,
         base_settings: utils.BaseSettings):
    logger = create_logger(__name__, base_settings.log_dir)

    try:
        if sync_type == 'hlr-proxy':
            sync_file_name = base_settings.hlr_proxy_file
            sync_file = base_settings.sync_dir.joinpath(sync_file_name)

            with open(sync_file, 'w') as sync_f:
                for file in handled_files:
                    with open(file, 'r') as handled_f:
                        for line in handled_f:
                            sync_f.write(line)

            utils.copy_to_smssw(str(sync_file), str(base_settings.remote_sync_dir.joinpath(sync_file_name)),
                                base_settings)
        elif sync_type == 'hlr-resale':
            sync_file_name = base_settings.hlr_resale_file
            files = os.listdir(base_settings.source_sync_dir)
            load_mode = define_load_mode(files)
            logger.info(f'load mode is {load_mode}')

            if load_mode == 'full':
                file_count = len(
                    list(filter(lambda n: n.startswith('Port_All') or n.startswith('Numbering_plan'), files)))
                if file_count < 2:
                    logger.info('not all files for full import arrived')
                    return

            for file in files:
                f = os.path.join(base_settings.source_sync_dir, file)
                with ZipFile(f) as zip_file:
                    zip_file.extractall(base_settings.source_sync_dir)
                os.remove(f)
            files = os.listdir(base_settings.source_sync_dir)
            tmp_file = base_settings.sync_dir.joinpath(f'tmp_{sync_file_name}')
            with open(tmp_file, 'wb') as out_f:
                # concatenate source files
                for source_file_name in files:
                    source_file_path = base_settings.source_sync_dir.joinpath(
                        str(source_file_name))
                    with open(source_file_path, 'rb') as in_f:
                        shutil.copyfileobj(in_f, out_f)
                    os.remove(source_file_path)
                # concatenate parsed files
                parsed_files = [base_settings.lat_conf.handled_file_path,
                                base_settings.kz_conf.handled_file_path,
                                base_settings.bel_conf.handled_file_path]
                for parsed_file in parsed_files:
                    if not parsed_file.exists():
                        continue
                    with open(parsed_file, 'rb') as in_f:
                        shutil.copyfileobj(in_f, out_f)

            source_sync_file = base_settings.sync_dir.joinpath(sync_file_name)
            with open(tmp_file, 'r') as source:
                reader = csv.reader(source, delimiter=';')
                with open(source_sync_file, "w") as destination:
                    writer = csv.writer(destination, delimiter=';')
                    for r in reader:
                        msisdn = r[0]
                        mccmnc = r[1]
                        port_time = r[2]
                        try:
                            owner_id = r[4]
                        except IndexError:
                            owner_id = None
                        if owner_id:
                            writer.writerow((msisdn,
                                             mccmnc,
                                             port_time,
                                             owner_id))
                        else:
                            writer.writerow((msisdn, mccmnc, port_time))
            os.remove(tmp_file)
            utils.copy_to_smssw(
                str(source_sync_file),
                str(base_settings.remote_sync_dir.joinpath(sync_file_name)),
                base_settings)
    except Exception as err:
        logger.exception(f'an error during sync\n\n{err}',
                         exc_info=True,
                         stack_info=True)
        raise exceptions.SyncMnpError(err) from None

    logger.info('finished sync')
