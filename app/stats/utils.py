import asyncio
import datetime
import multiprocessing as mp
import re
import time
from dataclasses import dataclass

import httpx

from app import models, service, database
from app.config import logger


# todo create process for updating stats for today

async def get_stats() -> list[dict]:
    async with httpx.AsyncClient() as cli:
        resp = await cli.get('https://k0d.info/aff.php', headers={'Apikey': '1488'})
        return resp.json()


async def get_api_model_items(api_data: list[dict]):
    return [models.ApiDataRow(**api_row) for api_row in api_data]


async def update_api_data():
    api_data: list[dict] = await get_stats()
    today = datetime.datetime.today()
    today_stats = list(filter(lambda row: row['date'] == today.strftime('%Y-%m-%d'), api_data))
    data_objects: list[models.ApiDataRow] = await get_api_model_items(today_stats)
    logger.info(f'{today_stats[0]=}')
    async with database.context_async_session() as session:
        await service.delete_today_api_data(session)
        await service.add_api_data(session, data_objects)


@dataclass
class RegexIn:
    string: str

    def __eq__(self, other: str) -> bool:
        return bool(re.compile(other).search(self.string))


def inf_update_stats():
    asyncio.run(update_api_data())


def update_stats():
    logger.info(f'creating stats update process...')

    def inf_check():
        while True:
            now = datetime.datetime.now()
            if now.second == 58:
                process = mp.Process(target=inf_update_stats)
                process.start()
                process.join()
            time.sleep(.5)

    p = mp.Process(target=inf_check)
    p.start()


if __name__ == '__main__':
    update_stats()
