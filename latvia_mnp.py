from pathlib import Path

import utils


def parse_file(file_in: Path):
    pass


def handle_file(base_settings, lat_settings):
    """
    move source file to tmp dir
    archive source file
    parse file
    copy parsed file to local storage, to local FTP storage
    push file via SSH
    """

    return None


if __name__ == '__main__':
    base_settings = utils.get_base_settings()
    lat_settings = utils.get_latvia_settings()
    handle_file(base_settings, lat_settings)



