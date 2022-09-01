import argparse
import pprint
import traceback
from pathlib import Path

from typing import NamedTuple, List

import belarus_mnp
import exceptions
import kazakhstan_mnp
import latvia_mnp
import settings
import utils
from utils.loger_util import create_logger


def pretty(d: NamedTuple, indent=0):
    for key, value in d._asdict().items():
        if isinstance(value, utils.LatSettings) or isinstance(value, utils.KztSettings) or isinstance(value, utils.BelSettings):
            print('-' * 60)
            print(f'{key}')
            pretty(value, indent+4)
        else:
            print(' ' * indent + f'{key}: ' + str(value))


def create_parser():
    parser = argparse.ArgumentParser(
        description='script for parse MNP files and load DB to server')
    parser.add_argument(
        '--country',
        nargs='?',
        required=False,
        help='country for processing',
    )
    parser.add_argument(
        '-config',
        help='return config for provided country or'
             ' base config if "base" specified',
        action='store_true',
    )
    parser.add_argument(
        '--supported-countries',
        nargs='?',
        const=True,
        help='return list of supporting country',
        metavar='supported_countries'
    )
    parser.add_argument(
        '--sync',
        help='join files from all DB in one file. Depending on sync type create '
             'new file with specific format. Copy file to smssw',
        choices=['hlr-proxy', 'hlr-resale'],
    )

    return parser


def kazakhstan_handler(base_settings):
    try:
        kazakhstan_mnp.processing_mnp(base_settings)
    except exceptions.MnpProcessingError as err:
        tb = traceback.format_exc()
        utils.send_email(text=f'{err}\n\n{tb})',
                         subject='Kazakhstan mnp parser error')


def belarus_handler(base_settings):
    try:
        belarus_mnp.processing_mnp(base_settings)
    except exceptions.CreateConfigDirError as err:
        tb = traceback.format_exc()
        utils.send_email(text=f'{err}\n\n{tb}',
                         subject='Belarus parser error')
    except exceptions.ConfigLoadError as err:
        tb = traceback.format_exc()
        utils.send_email(text=f'{err}\n\n{tb}',
                         subject='Belarus parser error')
    except exceptions.MnpProcessingError as err:
        tb = traceback.format_exc()
        utils.send_email(text=f'{err}\n\n{tb}',
                         subject='Belarus parser error')


def latvia_handler(base_settings):
    try:
        latvia_mnp.file_handler(base_settings)
    except exceptions.ConfigLoadError as err:
        tb = traceback.format_exc()
        utils.send_email(text=f'{err}\n\n{tb})',
                         subject='Latvia mnp parser error')
    except exceptions.CreateConfigDirError as err:
        tb = traceback.format_exc()
        utils.send_email(text=f'{err}\n\n{tb}',
                         subject='Latvia parser error')
    except exceptions.MnpProcessingError as err:
        tb = traceback.format_exc()
        utils.send_email(text=f'{err}\n\n{tb}',
                         subject='Latvia parser error')


def sync(handled_files: List[Path],
         sync_type: str,
         base_settings: utils.BaseSettings):
    logger = create_logger('sync', base_settings.log_dir)

    logger.info(f'start {sync_type} sync')
    try:
        if sync_type == 'hlr-proxy':
            sync_dir_name = base_settings.hlr_proxy_file
        else:
            sync_dir_name = base_settings.hlr_resale_file

        sync_file = base_settings.sync_dir.joinpath(sync_dir_name)

        with open(sync_file, 'w') as sync_f:
            for file in handled_files:
                with open(file, 'r') as handled_f:
                    for line in handled_f:
                        sync_f.write(line)

        utils.copy_to_smssw(str(sync_file), str(base_settings.remote_sync_dir.joinpath(sync_dir_name)), base_settings)
    except Exception as err:
        logger.exception(f'an error during sync\n\n{err}', exc_info=True, stack_info=True)
        raise exceptions.SyncMnpError(err) from None

    logger.info('finished sync')


def main():
    base_settings = utils.get_base_settings()
    parser = create_parser()
    args = parser.parse_args()

    if args.country == 'latvia':
        latvia_handler(base_settings)
    elif args.country == 'belarus':
        belarus_handler(base_settings)
    elif args.country == 'kazakhstan':
        kazakhstan_handler(base_settings)

    if args.config:
        pretty(base_settings, 0)

    if args.supported_countries:
        pprint.pprint(settings.SUPPORTED_COUNTRIES)

    if args.sync:
        try:
            handled_files = [
                base_settings.lat_conf.handled_file_path,
                base_settings.bel_conf.handled_file_path,
                base_settings.kz_conf.handled_file_path,
            ]

            sync(handled_files, args.sync, base_settings)
        except exceptions.SyncMnpError as err:
            tb = traceback.format_exc()
            utils.send_email(text=f'{err}\n\n{tb}',
                             subject='Synchronization error')


if __name__ == '__main__':
    main()
