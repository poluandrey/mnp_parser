import argparse
import traceback

import belarus_mnp
import exceptions
import kazakhstan_mnp
import latvia_mnp
import utils
from hlr_sync import sync
from utils.loger_util import create_logger
from utils.utils import show_config


def create_parser():
    parser = argparse.ArgumentParser(
        description='script for parse MNP files and load DB to server')
    parser.add_argument(
        '-c',
        '--country',
        required=False,
        help='country for processing',
    )
    parser.add_argument(
        '-config',
        help='return current configuration',
        action='store_true',
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


def main():
    logger = create_logger(__name__)
    base_settings = utils.get_base_settings()
    parser = create_parser()
    args = parser.parse_args()
    logger.info(f'script started with following arguments: {args}')

    if args.country == 'latvia':
        latvia_handler(base_settings)
    elif args.country == 'belarus':
        belarus_handler(base_settings)
    elif args.country == 'kazakhstan':
        kazakhstan_handler(base_settings)

    if args.config:
        show_config(base_settings, 0)

    if args.sync:
        try:
            handled_files = [
                base_settings.lat_conf.handled_file_path,
                base_settings.bel_conf.handled_file_path,
                base_settings.kz_conf.handled_file_path,
            ]
            logger.info('start sync')
            sync(handled_files, args.sync, base_settings)
            logger.info('finished sync')
        except exceptions.SyncMnpError as err:
            tb = traceback.format_exc()
            utils.send_email(text=f'{err}\n\n{tb}',
                             subject='Synchronization error')


if __name__ == '__main__':
    main()
