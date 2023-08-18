import configparser
import os
import pathlib

import loguru
from dotenv import load_dotenv
from fastapi.templating import Jinja2Templates
from notifiers.logging import NotificationHandler

load_dotenv()
config = configparser.ConfigParser()
config.add_section('general')
config['general'] = os.environ
environ = config['general']

PACKAGE_FOLDER = pathlib.Path(__file__).parent.parent
TARGETS_FOLDER = pathlib.Path(PACKAGE_FOLDER, 'targets')
if not TARGETS_FOLDER.exists():
    os.mkdir(TARGETS_FOLDER)

DEBUG = environ.getboolean('DEBUG', True)
if not DEBUG:
    HOST = environ.get('HOST', '0.0.0.0')
    PORT = environ.getint('PORT', '8181')
else:
    HOST = environ.get('TEST_HOST', 'localhost')
    PORT = environ.getint('TEST_PORT', '8281')

POSTGRES_DB = environ['POSTGRES_DB']
TG_LOGGING_LEVEL = environ['TG_LOGGING_LEVEL']
POSTGRES_PASSWORD = environ['POSTGRES_PASSWORD']
POSTGRES_USER = environ['POSTGRES_USER']
POSTGRES_HOST = environ['POSTGRES_HOST']
POSTGRES_PORT = environ.getint('POSTGRES_PORT')
ASYNC_DB_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
SYNC_DB_URL = f"postgresql+psycopg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

REDIS_PASSWORD = environ['REDIS_PASSWORD']
REDIS_HOST = environ['REDIS_HOST']
REDIS_PORT = environ.getint('REDIS_PORT')

BITLY_KEY = environ['BITLY_KEY']
STATS_APIKEY = environ['STATS_APIKEY']

logger = loguru.logger
logging_handler = NotificationHandler('telegram')
logger.add(logging_handler, level=TG_LOGGING_LEVEL)

templates_dir = pathlib.Path(PACKAGE_FOLDER, 'templates')
TEMPLATES = Jinja2Templates(directory=templates_dir)


FAILS_LIMIT: int = environ.getint('FAILS_LIMIT', -200)
breakpoint()
