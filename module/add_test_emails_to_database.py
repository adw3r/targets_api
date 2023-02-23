import sqlite3

import pandas as pd
from pathlib import Path

from config import TARGETS_FOLDER


def get_database(path: Path | str):
    with open(path, encoding='latin-1') as f:
        return f.read().split('\n')


def save_database(path: Path | str, list_to_save: list):
    with open(path, 'w', encoding='latin-1') as f:
        f.write('\n'.join(list_to_save))


def to_sql():
    dbs = [
        'test_alotof.csv',
        'test_dadru.csv',
        'test_dbru.csv',
        'test_fkasn23.csv',
        'test_g11mp2.csv',
        'test_pobcasn23.csv',
        'test_rub36.csv',
        'test_turk.csv',
    ]

    for db in dbs:
        db_path = db
        db_name = db.removesuffix('.csv').removeprefix('test_')
        print(db_name)
        create_table_query = f'''
--         CREATE TABLE if not exists emails (
            id INTEGER PRIMARY KEY AUTOINCREMENT, email ANY, status TEXT default NULL, utm_source TEXT
        # )'''

        with sqlite3.connect(r'C:\Users\Administrator\Desktop\targets_api\my_data.db') as connection:
            cursor = connection.cursor()
            # cursor.execute(create_table_query)
            users = pd.read_csv(rf'C:\Users\Administrator\Desktop\targets_api\targets\{db_path}',
                                names=['email', 'is_available', 'source'], on_bad_lines=lambda d: print(d),
                                engine='python')
            users['source'] = db_name
            users['is_available'] = True
            users.to_sql('emails', connection, if_exists='append', index=False, dtype={'email': 'TEXT'})
            print('success!')


def main():
    files = (
        'turk.csv',
        'rub36.csv',
        'pobcasn23.csv',
        'alotof.csv',
        'g11mp2.csv',
        'dbru.csv',
        'fkasn23.csv',
        'dadru.csv',
    )
    for file in files:
        print(file)
        file_name = file.removesuffix('.csv')
        original_list = get_database(Path(TARGETS_FOLDER, file))
        step = 500
        cc = step
        c = 1
        while cc < len(original_list):
            original_list.insert(cc, f'radarodionova71+{file_name}{c}@gmail.com')
            original_list.insert(cc, f'softumwork+{file_name}{c}@gmail.com')
            cc += step
            c += 1
        save_database(Path(TARGETS_FOLDER, f'test_{file_name}.csv'), original_list)


if __name__ == '__main__':
    to_sql()
