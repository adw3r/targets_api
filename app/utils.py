import asyncio
import logging
import os
import re
from dataclasses import dataclass
from pathlib import Path
from random import choice
from string import ascii_letters, digits

import httpx
import sqlalchemy

from app import config, database, models
from app.config import BITLY_KEY
from app.config import TARGETS_FOLDER


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
                   f'{utm_source}&utm_term={utm_term}#{await generate_text()}'.replace(' ', '+')  # todo refactor
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


async def async_main():
    factories = '''
bognewge:test_bognewge.csv
bognewtot:test_bognewtot.csv
bognewuk:test_bognewuk.csv
dadru:test_dadru.csv
dbru:test_dbru.csv
fkasn23:test_fkasn23.csv
fulljc:test_fulljc.csv
fullpa:test_fullpa.csv
fullpu:test_fullpu.csv
fullraj:test_fullraj.csv
fullxbtr:test_fullxbtr.csv
g11mp2:test_g11mp2.csv
polcen:test_polcen.csv
rub36:test_rub36.csv
yanonl:test_yanonl.csv
    '''.strip().split('\n')

    factories = {f[0]: {'filename': f[1]} for f in [f.split(':') for f in factories]}

    async def add_users(factory):
        async with database.context_async_session() as session:
            source = await session.scalar(sqlalchemy.select(models.Source).where(models.Source.source_name == factory))
            print(source)
            if not source:
                return
            targets_ = tuple(dict(email=email[:127], source_id=source.id, sent_counter=0)
                             for email in
                             tuple(get_database(Path(config.TARGETS_FOLDER, factories[factory]['filename']))))
            print(f'{len(targets_)!r}')
            try:
                await session.execute(sqlalchemy.insert(models.TargetEmail), targets_)
                await session.commit()
                print(f'finished {source}')
            except Exception as e:
                logging.exception(e)
                await session.rollback()

    tasks = tuple(add_users(factory) for factory in factories)
    await asyncio.gather(*tasks)


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


def sync_main():
    existing_test_files = set(
        [file.removeprefix('test_') for file in filter(lambda name: 'test_' in name, os.listdir(TARGETS_FOLDER))])
    existing_files = set(filter(lambda name: 'test_' not in name, os.listdir(TARGETS_FOLDER)))
    files = existing_files - existing_test_files

    for file in files:
        print(file)
        suffix = file.removesuffix('.csv')
        original_list = get_database(Path(TARGETS_FOLDER, file))
        updated_list = add_test_emails(emails_list=original_list, suffix=suffix)
        file = Path(TARGETS_FOLDER, f'test_{suffix}.csv')
        print(file)
        save_database(file, updated_list)
        try:
            session = database.AsyncSession().sync_session
            source = models.Source(source_name=suffix, text_id='eng')
            session.add(source)
            print(f'adding {source}')
            targets_ = tuple(models.TargetEmail(email=email, source=source) for email in updated_list)
            print(f'{len(targets_)=}')
            session.add_all(targets_)
            session.commit()
            print(f'finished {source}')
        except Exception as error:
            print(error)
            os.remove(file)


@dataclass
class regex_in:
    string: str

    def __eq__(self, other: str | re.Pattern):
        if isinstance(other, str):
            other = re.compile(other)
        return other.search(self.string) is not None


if __name__ == '__main__':
    asyncio.run(async_main())
