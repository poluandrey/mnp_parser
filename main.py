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
    try:
        lat_settings = utils.get_latvia_settings()
        base_settings = utils.get_base_settings()
        bel_settings = utils.get_belarus_settings()
    except exceptions.ConfigLoadError:
        tb = traceback.format_exc()
        utils.send_email(text=tb, subject='mnp parser error')
        sys.exit()
    try:
        utils.create_folder(base_settings)
        utils.create_folder(lat_settings)
        utils.create_folder(bel_settings)
    except exceptions.CreateConfigDirError:
        tb = traceback.format_exc()
        utils.send_email(text=tb, subject='mnp parser error')
        sys.exit()
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


if __name__ == '__main__':
    main()
