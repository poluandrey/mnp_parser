import argparse
import os
import sys
import traceback

import belarus_mnp
import exceptions
import latvia_mnp
import settings
import utils


def parse_args():
    parser = argparse.ArgumentParser(
        description='script for parse MNP files and load DB to server')
    parser.add_argument(
        '--country',
        help='country for load',
        choices=settings.SUPPORTED_COUNTRIES
    )
    args = parser.parse_args()
    return args


def main():
    base_settings, bel_settings, lat_settings = load_config()
    create_folders(base_settings)
    create_folders(lat_settings)
    create_folders(bel_settings)
    args = parse_args()
    if args.country == 'latvia':
        try:
            latvia_mnp.handle_file(base_settings, lat_settings)
        except exceptions.SourceMnpFileNotExists:
            print(f'{lat_settings.source_file_path} not exists')
        except Exception:
            tb = traceback.format_exc()
            utils.send_email(text=tb, subject='Latvia parser error')
            tmp_file = base_settings.tmp_dir.joinpath(
                lat_settings.source_file_name)
            if tmp_file.exists():
                os.remove(tmp_file)
    elif args.country == 'belarus':
        try:
            belarus_mnp.handle_file(base_settings, bel_settings)
        except exceptions.SourceMnpFileNotExists as err:
            print(err)


def create_folders(config):
    try:
        utils.create_folder(config)
    except exceptions.CreateConfigDirError:
        tb = traceback.format_exc()
        utils.send_email(text=tb, subject='mnp parser error')
        sys.exit()


def load_config():
    try:
        lat_settings = utils.get_latvia_settings()
        base_settings = utils.get_base_settings()
        bel_settings = utils.get_belarus_settings()
    except exceptions.ConfigLoadError:
        tb = traceback.format_exc()
        utils.send_email(text=tb, subject='mnp parser error')
        sys.exit()
    return base_settings, bel_settings, lat_settings


if __name__ == '__main__':
    main()
