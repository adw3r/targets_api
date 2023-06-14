import os
from pathlib import Path

from sqlalchemy import select

from app import database, models
from app.config import TARGETS_FOLDER, logger


def add_targets_to_db(source_name, lang, csv_file_name):
    path_to_csv_file_with_emails = Path(TARGETS_FOLDER, csv_file_name)

    with database.create_sync_session() as db_session:
        source: models.Source | None = db_session.scalar(
            select(models.Source).where(models.Source.source_name == source_name))
        if not source:
            text = db_session.scalar(select(models.Text).where(models.Text.lang == lang))
            if not text:
                raise Exception(f'Language not exists! {lang!r}')
            source = models.Source(source_name=source_name)
            source.text_id = text.id
            db_session.add(source)
            db_session.commit()
            db_session.refresh(source)
    logger.info(f'{source.id, source}')
    with open(path_to_csv_file_with_emails) as file:
        emails = file.read().split('\n')
    new_emails = add_test_emails(emails, source_name)
    temp_file_path = Path(TARGETS_FOLDER, f'temp_{path_to_csv_file_with_emails.name}')
    with open(temp_file_path, 'w') as file:
        file.write('\n'.join([f'{email},{source.id}' for email in new_emails]))
    logger.info(f'{temp_file_path}')
    copy_from_csv(temp_file_path)
    os.remove(temp_file_path)


def add_test_emails(emails_list: list, suffix) -> list:
    updated_list = emails_list.copy()
    step = 500
    cc = step
    c = 1
    while cc < len(updated_list):
        updated_list.insert(cc, f'softumwork+{suffix}{c}@gmail.com')
        # updated_list.insert(cc, f'wooterx+{suffix}{c}@gmail.com')
        cc += step
        c += 1
    return updated_list


def copy_from_csv(path_to_file):
    with database.create_sync_session() as session:
        with session.connection().connection.cursor() as cur:
            with open(path_to_file) as file:
                with cur.copy("COPY target_emails(email,source_id) from stdin DELIMITER ','") as copy:
                    copy.write(file.read())
            session.commit()
