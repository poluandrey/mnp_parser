import argparse
import os
import traceback

import belarus_mnp
import exceptions
import kazakhstan_mnp
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


def kazakhstan_handler(base_settings):
    try:
        kzt_settings = utils.get_kazakhstan_settings()
        utils.create_folder(kzt_settings)
    except exceptions.ConfigLoadError:
        print('error during load latvia settings')
    except exceptions.CreateConfigDirError:
        print('error during create KZT folder')


def belarus_handler(base_settings):
    try:
        bel_settings = utils.get_belarus_settings()
        utils.create_folder(bel_settings)
        belarus_mnp.handle_file(base_settings, bel_settings)
    except exceptions.SourceMnpFileNotExists as err:
        print(err)
    except exceptions.MoreThanOneSourceFilesFound as err:
        print(err)


def latvia_handler(base_settings):
    try:
        lat_settings = utils.get_latvia_settings()
        utils.create_folder(lat_settings)
        latvia_mnp.handle_file(base_settings, lat_settings)
    except exceptions.ConfigLoadError:
        print('error during load latvia settings')
    except exceptions.SourceMnpFileNotExists:
        print(f'{lat_settings.source_file_path} not exists')
    except Exception:
        tb = traceback.format_exc()
        utils.send_email(text=tb, subject='Latvia parser error')
        tmp_file = base_settings.tmp_dir.joinpath(
            lat_settings.source_file_name)
        if tmp_file.exists():
            os.remove(tmp_file)


def main():
    base_settings = utils.get_base_settings()
    utils.create_folder(base_settings)
    args = parse_args()
    if args.country == 'latvia':
        latvia_handler(base_settings)
    elif args.country == 'belarus':
        belarus_handler(base_settings)
    elif args.country == 'kazakhstan':
        kazakhstan_handler(base_settings)


if __name__ == '__main__':
    main()
