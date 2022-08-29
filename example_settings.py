import pathlib

BASE_DIR = pathlib.Path(__file__).parent
FILE_STORAGE = pathlib.Path('/var/log/mnp')
TMP_DIR = FILE_STORAGE.joinpath('tmp')
LOG_DIR = FILE_STORAGE.joinpath('log')
ARCHIVE_DIR = FILE_STORAGE.joinpath('archive')
SUPPORTED_COUNTRIES = ('latvia', 'belarus', 'kazakhstan')

# email settings for local notification
EMAIL_SERVER = 'test.email.com'
EMAIL_PORT = 587
EMAIL_LOGIN = 'test_user@test.com'
EMAIL_PASSWORD = 'password'
EMAIL_RECIPIENTS = ['test_user@test.com']

# smssw ssh server settings
SSH_SERVER = '192.168.0.1'
SSH_PORT = 22
SSH_USER = 'test_user'

# Latvia settings
# path tp directory with source file
LAT_SOURCE_DIR = FILE_STORAGE.joinpath('latvia_source')
# source file name
LAT_SOURCE_FILE_NAME = 'mnp_latvia.csv'
# path to directory with parsed mnp file
LAT_HANDLED_FILE_DIR = FILE_STORAGE.joinpath('latvia')
# parsed mnp file name
LAT_HANDLED_FILE_NAME = 'lat_mnp.csv'
# path to archive directory
LAT_ARCHIVE_DIR = ARCHIVE_DIR.joinpath('latvia')
# local FTP storage
LAT_FTP_DIR = FILE_STORAGE.joinpath('ftp', 'latvia')
LAT_FTP_GROUP_ID = 999
# smssw remote folder for MNP DB load
LAT_REMOTE_DIR = ...


# Belarus settings
# path tp directory with source file
BEL_SOURCE_DIR = FILE_STORAGE.joinpath('belarus_source')
# source file mask which will use to find file in source dir
BEL_SOURCE_FILE_MASK = 'MNP_BY_*.xlsx'
# directory where parsed file stored
BEL_HANDLED_FILE_DIR = FILE_STORAGE.joinpath('belarus')
# parsed file name
BEL_HANDLED_FILE_NAME = 'bel_mnp.csv'
BEL_ARCHIVE_DIR = ARCHIVE_DIR.joinpath('belarus')
# local FTP storage
BEL_FTP_DIR = FILE_STORAGE.joinpath('ftp', 'belarus')
# local FTP group id
BEL_FTP_GROUP_ID = 998
# remote folder in smssw
BEL_REMOTE_DIR = ...

# Kazakhstan settings
KZT_HANDLED_FILE_DIR = FILE_STORAGE.joinpath('kazakhstan')
KZT_HANDLED_FILE_NAME = 'kzt_mnp.csv'
KZT_ARCHIVE_DIR = ARCHIVE_DIR.joinpath('kazakhstan')
KZT_SSH_SERVER = '192.168.0.1'
KZT_SSH_PORT = 22
KZT_SSH_USER = 'test_user'
KZT_SSH_PASSWD = 'test_password'
# local FTP storage
KZT_FTP_DIR = FILE_STORAGE.joinpath('ftp', 'kazakhstan')
KZT_FTP_GROUP_ID = 997
# remote folder for MNP DB load
KZT_REMOTE_DIR = ...
