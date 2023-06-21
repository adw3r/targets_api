import os
from pathlib import Path

from sqlalchemy import select

from app import database, models
from app.config import TARGETS_FOLDER, logger

ENCODING = 'latin-1'

DELIMITER = ','


def add_targets_to_db(source_name, lang, input_file_name):
    path_to_csv_file_with_emails = Path(TARGETS_FOLDER, input_file_name)

    source = get_source(lang, source_name)
    logger.info(f'{source.id, source}')
    with open(path_to_csv_file_with_emails, encoding=ENCODING) as file:
        emails = [clean_email(email) for email in set(file.read().strip().split('\n')) if email]

    add_test_emails(emails, source_name)
    temp_file_path = Path(TARGETS_FOLDER, f'temp_{path_to_csv_file_with_emails.name}')
    with open(temp_file_path, 'w', encoding=ENCODING) as file:
        file.write('\n'.join([f'{email}{DELIMITER}{source.id}' for email in emails]))
    logger.info(f'{temp_file_path}')
    copy_from_csv(temp_file_path)
    os.remove(temp_file_path)


def clean_email(email: str) -> str:
    email = email.replace(DELIMITER, '')
    email = email.replace('\\', '')
    return email[:127]


def get_source(lang, source_name):
    with database.create_sync_session() as db_session:
        source: models.Source | None = db_session.scalar(
            select(models.Source).where(models.Source.source_name == source_name))
        if not source:
            text = db_session.scalar(select(models.Text).where(models.Text.lang == lang))
            if not text:
                raise Exception(f'Language not exists! {lang!r}')
            source = models.Source(source_name=source_name, is_available=False)
            source.text_id = text.id
            db_session.add(source)
            db_session.commit()
            db_session.refresh(source)
    return source


def add_test_emails(emails_list: list, suffix) -> list:  # refactor
    step = 500

    c = step
    suffix_index = 1
    while c < len(emails_list):
        emails_list.insert(c, f'softumwork+{suffix}{suffix_index}@gmail.com')
        # updated_list.insert(cc, f'wooterx+{suffix}{c}@gmail.com')
        c += step
        suffix_index += 1
    return emails_list


def copy_from_csv(path_to_file):
    with database.create_sync_session() as session:
        with session.connection().connection.cursor() as cur:
            with cur.copy(f"COPY target_emails(email,source_id) from stdin DELIMITER '{DELIMITER}'") as copy:
                with open(path_to_file, encoding=ENCODING) as file:
                    copy.write(file.read())
            session.commit()
