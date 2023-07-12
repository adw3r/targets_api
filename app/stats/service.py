import dataclasses
import datetime
import re

import httpx
from sqlalchemy import select, text, delete, func, extract
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.config import STATS_APIKEY


async def get_api_model_items(api_data: list[dict]):
    return [models.ApiDataRow(**api_row) for api_row in api_data]


async def get_stats() -> list[dict]:
    async with httpx.AsyncClient() as cli:
        resp = await cli.get('https://k0d.info/aff.php', headers={'Apikey': STATS_APIKEY})
        return resp.json()


@dataclasses.dataclass
class RegexIn:
    string: str

    def __eq__(self, other: str) -> bool:
        return bool(re.compile(other).search(self.string))


@dataclasses.dataclass(frozen=True, slots=True)
class RegApiData:
    regs: int
    data: datetime.datetime


async def delete_month_api_data(session: AsyncSession):
    time = datetime.datetime.now()
    criteria = extract('month', models.ApiDataRow.date) == time.month
    await session.execute(delete(models.ApiDataRow).where(criteria))
    await session.commit()


async def add_api_data(session: AsyncSession, data_objects: list[models.ApiDataRow]):
    session.add_all(data_objects)
    await session.commit()


async def get_api_data(session: AsyncSession) -> list[RegApiData]:
    stmt = '''
        select sum(registration) as reg, date from api_stats group by date order by date desc
    '''
    res = await session.execute(text(stmt))
    return [RegApiData(*i) for i in res.all()]


async def get_regs_stat_for_current_month(session: AsyncSession):
    date = datetime.datetime.today()
    res = await session.scalars(
        select(models.ApiDataRow).filter(
            func.date_trunc('month', models.ApiDataRow.date) == func.date_trunc('month', date),
            # func.date_trunc('day', models.ApiDataRow.date) == func.date_trunc('day', date),
            # func.date_trunc('year', models.ApiDataRow.date) == func.date_trunc('year', date),
        )
    )
    return res.all()


async def get_regs_stat_for_today(session: AsyncSession):
    res = await session.scalars(select(models.ApiDataRow).where(models.ApiDataRow.date == func.current_date()))
    return res.all()


async def hit_stats(session: AsyncSession):
    statement = text('select sum(hits) as hits, utm_term from api_stats group by utm_term order by hits desc')
    res = await session.execute(statement)
    return [{'utm_term': i[1], 'hits': i[0]} for i in res.fetchall()]


async def get_regs_stat_for_specific_date(session: AsyncSession, date):
    date = datetime.datetime.strptime(date, '%Y-%m-%d')
    res = await session.scalars(
        select(models.ApiDataRow).where(
            func.date_trunc('month', models.ApiDataRow.date) == func.date_trunc('month', date),
            func.date_trunc('day', models.ApiDataRow.date) == func.date_trunc('day', date),
            func.date_trunc('year', models.ApiDataRow.date) == func.date_trunc('year', date)
        )
    )
    return res.all()
