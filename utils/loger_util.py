import logging
from utils.utils import get_base_settings
from pathlib import Path

base_settings = get_base_settings()


def create_logger(logger_name: str, logger_path: Path = base_settings.log_dir) -> logging.Logger:
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    fh = logging.FileHandler(logger_path.joinpath(f'{logger_name}.log'))
    fh.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    fh.setFormatter(formatter)

    logger.addHandler(fh)
    return logger
