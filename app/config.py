import configparser
import os
import pathlib

from dotenv import load_dotenv

import loguru

load_dotenv()

PACKAGE_FOLDER = pathlib.Path(__file__).parent.parent
TARGETS_FOLDER = pathlib.Path(PACKAGE_FOLDER, 'targets')
if not TARGETS_FOLDER.exists():
    os.mkdir(TARGETS_FOLDER)

config = configparser.ConfigParser()
config.read(pathlib.Path(PACKAGE_FOLDER, 'config.ini'))

config['general']['DEBUG'] = os.environ.get('DEBUG', 'False')
DEBUG = config['general'].getboolean('DEBUG', False)

if not DEBUG:
    HOST = config['general'].get('HOST', '0.0.0.0')
    PORT = config['general'].getint('PORT', 8181)
else:
    HOST = config['general'].get('TEST_HOST', '0.0.0.0')
    PORT = config['general'].getint('TEST_PORT', 8281)

POSTGRES_DB = os.environ['POSTGRES_DB']
POSTGRES_PASSWORD = os.environ['POSTGRES_PASSWORD']
POSTGRES_USER = os.environ['POSTGRES_USER']
POSTGRES_HOST = os.environ['POSTGRES_HOST']
POSTGRES_PORT = os.environ['POSTGRES_PORT']

REDIS_PASSWORD = os.environ['REDIS_PASSWORD']
REDIS_HOST = os.environ['REDIS_HOST']
REDIS_PORT = os.environ['REDIS_PORT']

ASYNC_DB_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
SYNC_DB_URL = f"postgresql+psycopg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
BITLY_KEY = os.environ['BITLY_KEY']

logger = loguru.logger