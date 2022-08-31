import pathlib

from dotenv import dotenv_values

BASE_DIR = pathlib.Path(__file__).parent
config = dotenv_values(BASE_DIR.joinpath('.env'))

FILE_STORAGE = pathlib.Path(config['FILES_STORAGE'])
TMP_DIR = FILE_STORAGE.joinpath('tmp')
LOG_DIR = FILE_STORAGE.joinpath('log')
ARCHIVE_DIR = FILE_STORAGE.joinpath('archive')
SYNC_DIR = FILE_STORAGE.joinpath('sync')
HLR_PROXY_FILE = 'hlr-proxy.csv'
HLR_RESALE_FILE = 'hlr-resale.csv'
SUPPORTED_COUNTRIES = list(config['SUPPORTED_COUNTRIES'].replace(' ', '').split(sep=','))

# email settings for local notification
EMAIL_SERVER = config['EMAIL_SERVER']
EMAIL_PORT = int(config['EMAIL_PORT'])
EMAIL_LOGIN = config['EMAIL_LOGIN']
EMAIL_PASSWORD = config['EMAIL_PASSWORD']
EMAIL_RECIPIENTS = config['EMAIL_RECIPIENTS'].replace(' ', '').split(sep=',')

# smssw ssh server settings
SSH_SERVER = config['SSH_SERVER']
SSH_PORT = int(config['SSH_PORT'])
SSH_USER = config['SSH_USER']

# Latvia settings
# path tp directory with source file
LAT_SOURCE_DIR = pathlib.Path(config['LAT_SOURCE_DIR'])
# source file name
LAT_SOURCE_FILE_NAME = config['LAT_SOURCE_FILE_NAME']
# path to directory with parsed mnp file
LAT_HANDLED_FILE_DIR = FILE_STORAGE.joinpath('latvia')
# parsed mnp file name
LAT_HANDLED_FILE_NAME = config['LAT_HANDLED_FILE_NAME']
# path to archive directory
LAT_ARCHIVE_DIR = ARCHIVE_DIR.joinpath('latvia')
# local FTP storage
LAT_FTP_DIR = config['LAT_FTP_DIR']
LAT_FTP_GROUP_ID = int(config['LAT_FTP_GROUP_ID'])
# smssw remote folder for MNP DB load
LAT_REMOTE_DIR = pathlib.Path(config['LAT_REMOTE_DIR'])

# Belarus settings
# path tp directory with source file
BEL_SOURCE_DIR = pathlib.Path(config['BEL_SOURCE_DIR'])
# source file mask which will use to find file in source dir
BEL_SOURCE_FILE_MASK = config['BEL_SOURCE_FILE_MASK']
# directory where parsed file stored
BEL_HANDLED_FILE_DIR = FILE_STORAGE.joinpath('belarus')
# parsed file name
BEL_HANDLED_FILE_NAME = config['BEL_HANDLED_FILE_NAME']
BEL_ARCHIVE_DIR = ARCHIVE_DIR.joinpath('belarus')
# local FTP storage
BEL_FTP_DIR = pathlib.Path(config['BEL_FTP_DIR'])
# local FTP group id
BEL_FTP_GROUP_ID = int(config['BEL_FTP_GROUP_ID'])
# remote folder in smssw
BEL_REMOTE_DIR = pathlib.Path(config['BEL_REMOTE_DIR'])

# Kazakhstan settings
KZT_HANDLED_FILE_DIR = FILE_STORAGE.joinpath('kazakhstan')
KZT_HANDLED_FILE_NAME = config['KZT_HANDLED_FILE_NAME']
KZT_ARCHIVE_DIR = ARCHIVE_DIR.joinpath('kazakhstan')
KZT_SSH_SERVER = config['KZT_SSH_SERVER']
KZT_SSH_PORT = int(config['KZT_SSH_PORT'])
KZT_SSH_USER = config['KZT_SSH_USER']
KZT_SSH_PASSWD = config['KZT_SSH_PASSWD']
# local FTP storage
KZT_FTP_DIR = pathlib.Path(config['KZT_FTP_DIR'])
KZT_FTP_GROUP_ID = int(config['KZT_FTP_GROUP_ID'])
# remote folder for MNP DB load
KZT_REMOTE_DIR = config['KZT_REMOTE_DIR']
