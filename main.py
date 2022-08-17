import argparse
import sys
import traceback

import exceptions
import settings
from mnp_parser import mnp_handler
from utils import check_settings, send_email


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
        check_settings()
    except exceptions.CheckConfigError:
        tb = traceback.format_exc()
        send_email(text=tb, subject='mnp parser error')
        sys.exit()
    args = parse_args()
    mnp_handler.parser(country=args.country)


if __name__ == '__main__':
    main()
