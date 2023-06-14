import configparser
import os
import pathlib

import loguru
from dotenv import load_dotenv

load_dotenv()
config = configparser.ConfigParser()
config.add_section('general')
config['general'] = os.environ
environ = config['general']

PACKAGE_FOLDER = pathlib.Path(__file__).parent.parent
TARGETS_FOLDER = pathlib.Path(PACKAGE_FOLDER, 'targets')
if not TARGETS_FOLDER.exists():
    os.mkdir(TARGETS_FOLDER)


DEBUG = config['general'].getboolean('DEBUG', True)
if not DEBUG:
    HOST = environ.get('HOST', '0.0.0.0')
    PORT = config['general'].get('PORT', '8181')
else:
    HOST = config['general'].getint('TEST_HOST', 'localhost')
    PORT = environ.getint('TEST_PORT', '8281')

POSTGRES_DB = environ['POSTGRES_DB']
POSTGRES_PASSWORD = environ['POSTGRES_PASSWORD']
POSTGRES_USER = environ['POSTGRES_USER']
POSTGRES_HOST = environ['POSTGRES_HOST']
POSTGRES_PORT = environ['POSTGRES_PORT']
ASYNC_DB_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
SYNC_DB_URL = f"postgresql+psycopg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

REDIS_PASSWORD = environ['REDIS_PASSWORD']
REDIS_HOST = environ['REDIS_HOST']
REDIS_PORT = environ['REDIS_PORT']

BITLY_KEY = environ['BITLY_KEY']
STATS_APIKEY = environ['STATS_APIKEY']

logger = loguru.logger
