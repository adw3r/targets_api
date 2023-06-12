import re
from dataclasses import dataclass
from pathlib import Path
from random import choice
from string import ascii_letters, digits

import httpx
from sqlalchemy import select

from app import database, models
from app.config import BITLY_KEY, TARGETS_FOLDER, logger


def get_database(path: Path | str):
    with open(path, encoding='latin-1') as f:
        return f.read().split('\n')


def save_database(path: Path | str, list_to_save: list):
    with open(path, 'w', encoding='latin-1') as f:
        f.write('\n'.join(list_to_save))


async def create_link(link_to_short) -> httpx.Response:
    headers = {
        'Authorization': f'Bearer {BITLY_KEY}',
    }
    json_data = {
        'long_url': link_to_short,
        'domain': 'bit.ly'
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url='https://api-ssl.bitly.com/v4/bitlinks', headers=headers, json=json_data)
        return response


async def get_link_summary(bitly_link: str, time_unit: str = 'month') -> dict:
    '''

    :param bitly_link: format of bit.ly/3oB8qmJ
    :return:
    '''
    headers = {
        'Authorization': f'Bearer {BITLY_KEY}',
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f'https://api-ssl.bitly.com/v4/bitlinks/{bitly_link}/clicks/summary?unit={time_unit}',
            headers=headers)
        return response.json()


async def generate_text(length: int = 6, sequence=ascii_letters + digits):
    return ''.join([choice(sequence) for _ in range(length)])


async def get_link_from_bitly(utm_link: str, utm_source: str, utm_campaign: str, utm_term: str) -> httpx.Response:
    project_link = f'{utm_link}&utm_campaign={utm_campaign}&utm_source=' \
                   f'{utm_source}&utm_term={utm_term}#{await generate_text()}'.replace(' ', '+')  # refactor
    params = {
        # "group_guid": "Ba1bc23dE4F",
        "domain": "bit.ly",
        "long_url": project_link
    }
    async with httpx.AsyncClient() as client:
        response = await client.post('https://api-ssl.bitly.com/v4/shorten', json=params,
                                     headers={'Authorization': f'Bearer {BITLY_KEY}'})
    return response


async def get_stats() -> list[dict]:
    async with httpx.AsyncClient() as cli:
        resp = await cli.get('https://k0d.info/aff.php', headers={'Apikey': '1488'})
        return resp.json()


async def get_api_model_items(api_data: list[dict]):
    return [models.ApiDataRow(**api_row) for api_row in api_data]


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
    # os.remove(temp_file_path)


def add_test_emails(emails_list: list, suffix) -> list:
    updated_list = emails_list.copy()
    step = 500
    cc = step
    c = 1
    while cc < len(updated_list):
        updated_list.insert(cc, f'softumwork+{suffix}{c}@gmail.com')
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


@dataclass
class regex_in:
    string: str

    def __eq__(self, other: str | re.Pattern):
        if isinstance(other, str):
            other = re.compile(other)
        return other.search(self.string) is not None
