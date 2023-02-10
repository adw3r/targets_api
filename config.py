import configparser
import os
import pathlib

PACKAGE_FOLDER = pathlib.Path(__file__).parent
TARGETS_FOLDER = pathlib.Path(PACKAGE_FOLDER, 'targets')
if not TARGETS_FOLDER.exists():
    os.mkdir(TARGETS_FOLDER)

config = configparser.ConfigParser()
config.read(pathlib.Path(PACKAGE_FOLDER, 'config.ini'))

HOST = config['general'].get('HOST', 'localhost')
PORT = config['general'].getint('PORT', 8181)
