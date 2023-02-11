import configparser
import os
import pathlib

from dotenv import load_dotenv


load_dotenv()

PACKAGE_FOLDER = pathlib.Path(__file__).parent
TARGETS_FOLDER = pathlib.Path(PACKAGE_FOLDER, 'targets')
if not TARGETS_FOLDER.exists():
    os.mkdir(TARGETS_FOLDER)

config = configparser.ConfigParser()
config.read(pathlib.Path(PACKAGE_FOLDER, 'config.ini'))

config['general']['DEBUG'] = os.environ.get('DEBUG', 'False')
DEBUG = config['general'].getboolean('DEBUG')

if not DEBUG:
    HOST = config['general'].get('HOST', '0.0.0.0')
    PORT = config['general'].getint('PORT', 8181)
else:
    HOST = config['general'].get('TEST_HOST', 'localhost')
    PORT = config['general'].getint('TEST_PORT', 8281)
