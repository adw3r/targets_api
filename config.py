import configparser
import os
import pathlib

from dotenv import load_dotenv


load_dotenv()

PACKAGE_FOLDER = pathlib.Path(__file__).parent
TARGETS_FOLDER = pathlib.Path(PACKAGE_FOLDER, 'targets')
SQLALCHEMY_DB_URL = f'sqlite:///{PACKAGE_FOLDER}/my_data.db'


if not TARGETS_FOLDER.exists():
    os.mkdir(TARGETS_FOLDER)

config = configparser.ConfigParser()
config.read(pathlib.Path(PACKAGE_FOLDER, 'config.ini'))
config_general = config['general']

config_general['DEBUG'] = os.environ.get('DEBUG', 'False')
DEBUG = config_general.getboolean('DEBUG')
REDIS_HOST = config_general.get('REDIS_HOST', 'localhost')


if not DEBUG:
    HOST = config_general.get('HOST', '0.0.0.0')
    PORT = config_general.getint('PORT', 8181)
else:
    HOST = config_general.get('TEST_HOST', 'localhost')
    PORT = config_general.getint('TEST_PORT', 8281)
