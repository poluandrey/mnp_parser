import os
import shutil
from pathlib import Path

import exceptions
import utils


def parse_file(file_in: Path) -> Path:
    """:return file_out: Path"""
    pass


def handle_file(base_settings: utils.BaseSettings,
                lat_settings: utils.LatSettings):
    """
    move source file to tmp dir
    archive source file
    parse file
    copy parsed file to local storage
    push file via SSH
    """
    if not lat_settings.source_file_path.exists():
        raise exceptions.SourceMnpFileNotExists(
            f'{lat_settings.source_file_path} does not exists')
    tmp_file = shutil.copy(lat_settings.source_file_path,
                           base_settings.tmp_dir)
    utils.archive_file(file_in=lat_settings.source_file_path,
                       archive_dir=lat_settings.archive_dir)

    parsed_file = parse_file(tmp_file)

    shutil.copy(parsed_file, lat_settings.handled_file_dir)
    utils.push_file_to_server(file_in=parsed_file,
                              remoute_dir=lat_settings.remote_dir)
    os.remove(tmp_file)
    return tmp_file


if __name__ == '__main__':
    b_settings = utils.get_base_settings()
    l_settings = utils.get_latvia_settings()
    handle_file(base_settings=b_settings,
                lat_settings=l_settings)
