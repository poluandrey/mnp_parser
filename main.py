import argparse
import pprint
import traceback

import belarus_mnp
import exceptions
import kazakhstan_mnp
import latvia_mnp
import settings
import utils


def create_parser():
    parser = argparse.ArgumentParser(
        description='script for parse MNP files and load DB to server')
    parser.add_argument(
        '--country',
        help='country for processing',
    )
    parser.add_argument(
        '--check-config',
        help='return config for provided country or'
             ' base config if "base" specified',
        metavar='check_config'
    )
    parser.add_argument(
        '--supported-countries',
        nargs='?',
        const=True,
        help='return list of supporting country',
        metavar='supported_countries'
    )

    return parser


def kazakhstan_handler(base_settings):
    try:
        kzt_settings = utils.get_kazakhstan_settings()
        utils.create_folder(kzt_settings)
        kazakhstan_mnp.processing_mnp(base_settings, kzt_settings)
    except exceptions.CreateConfigDirError:
        print('error during create KZ folders')
    except exceptions.ConfigLoadError:
        print('error during load kazakhstan settings')
    except exceptions.MnpProcessingError as err:
        tb = traceback.format_exc()
        utils.send_email(text=f'{err}\n\n{tb})',
                         subject='Kazakhstan mnp parser error')


def belarus_handler(base_settings):
    try:
        bel_settings = utils.get_belarus_settings()
        utils.create_folder(bel_settings)
        belarus_mnp.processing_mnp(base_settings, bel_settings)
    except exceptions.CreateConfigDirError:
        print('error during create BEL folders')
    except exceptions.ConfigLoadError:
        print('error during load belarus settings')
    except exceptions.SourceFileError as err:
        utils.send_email(text=f'Belarus source file error\n\n{err}',
                         subject='Belarus parser error')
    except exceptions.MnpProcessingError as err:
        tb = traceback.format_exc()
        utils.send_email(text=f'{err}\n\n{tb}',
                         subject='Belarus parser error')


def latvia_handler(base_settings):
    try:
        lat_settings = utils.get_latvia_settings()
        utils.create_folder(lat_settings)
        latvia_mnp.file_handler(base_settings, lat_settings)
    except exceptions.ConfigLoadError as err:
        tb = traceback.format_exc()
        utils.send_email(text=f'{err}\n\n{tb})',
                         subject='Latvia mnp parser error')
    except exceptions.SourceFileError as err:
        utils.send_email(text=f'latvia source file error\n\n{err}',
                         subject='Latvia mnp parser error')
    except exceptions.MnpProcessingError as err:
        tb = traceback.format_exc()
        utils.send_email(text=f'{err}\n\n{tb}',
                         subject='Latvia parser error')


def main():
    base_settings = utils.get_base_settings()
    utils.create_folder(base_settings)
    parser = create_parser()
    args = parser.parse_args()
    if args.country == 'latvia':
        latvia_handler(base_settings)
    elif args.country == 'belarus':
        belarus_handler(base_settings)
    elif args.country == 'kazakhstan':
        kazakhstan_handler(base_settings)
    else:
        print('unsupported country. Use --supported-country')

    if args.check_config == 'base':
        pprint.pprint(dict(base_settings._asdict()), indent=4)
    elif args.check_config == 'latvia':
        lat_settings = utils.get_latvia_settings()
        pprint.pprint(dict(lat_settings._asdict()), indent=4)
    elif args.check_config == 'kazakhstan':
        lat_settings = utils.get_kazakhstan_settings()
        pprint.pprint(dict(lat_settings._asdict()), indent=4)
    elif args.check_config == 'belarus':
        lat_settings = utils.get_belarus_settings()
        pprint.pprint(dict(lat_settings._asdict()), indent=4)

    if args.supported_countries:
        pprint.pprint(settings.SUPPORTED_COUNTRIES)


if __name__ == '__main__':
    main()
