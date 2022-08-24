import csv
import os
import shutil
from datetime import datetime
from glob import glob
from pathlib import Path

import openpyxl

import exceptions
import utils


def parse_file(file_in, bel_settings):
    wb = openpyxl.load_workbook(file_in)
    sheet = wb['Sheet1']
    rows = []
    for row in sheet.iter_rows(0, sheet.max_row):
        data = []
        for cell in row:
            data.append(cell.value)
        rows.append(data)
    del rows[0]
    for row in rows:
        row[0] = f'2570{row[0]}'
        row[2] = int(datetime.strptime(row[2],
                                       '%d.%m.%Y %H:%M:%S').timestamp())
        row[0], row[1] = row[1], row[0]
    with open(bel_settings.handled_file_path, 'w') as mnp_db:
        csv_f = csv.writer(mnp_db, delimiter=';')
        csv_f.writerows(rows)


def handle_file(base_settings: utils.BaseSettings,
                bel_settings: utils.BelSettings):

    source_file_mask = bel_settings.source_dir.joinpath(bel_settings.source_file_mask)
    source_files = glob(str(source_file_mask))
    if not source_files:
        raise exceptions.SourceMnpFileNotExists('does not found files matching patterns')
    elif len(source_files) != 1:
        raise exceptions.MoreThanOneSourceFilesFound('to many source files found')
    source_file = Path(source_files[0])

    tmp_file = shutil.copy(source_file, base_settings.tmp_dir)
    utils.archive_file(source_file, bel_settings.archive_dir)
    
    if bel_settings.handled_file_path.exists():
        utils.archive_file(bel_settings.handled_file_path.exists, bel_settings.archive_dir)
        
    parse_file(tmp_file, bel_settings)

    utils.copy_to_smssw(bel_settings.handled_file_path, bel_settings.remote_dir)

    os.remove(tmp_file)
