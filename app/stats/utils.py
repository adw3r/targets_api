import re
import datetime
from dataclasses import dataclass

import httpx

from app import models, service, database


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
    async with database.context_async_session() as session:
        await service.delete_today_api_data(session)
        await service.add_api_data(session, data_objects)


@dataclass
class RegexIn:
    string: str

    def __eq__(self, other: str | re.Pattern):
        if isinstance(other, str):
            other = re.compile(other)
        return other.search(self.string) is not None
