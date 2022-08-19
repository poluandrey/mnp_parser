import argparse
import sys
import traceback

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
    except exceptions.ConfigLoadError:
        tb = traceback.format_exc()
        utils.send_email(text=tb, subject='mnp parser error')
        sys.exit()
    try:
        utils.create_folder(base_settings)
        utils.create_folder(lat_settings)
    except exceptions.CreateConfigDirError:
        tb = traceback.format_exc()
        utils.send_email(text=tb, subject='mnp parser error')
        sys.exit()
    args = parse_args()
    if args.country == 'latvia':
        latvia_mnp.handle_file(base_settings, lat_settings)


if __name__ == '__main__':
    main()
