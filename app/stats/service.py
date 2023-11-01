import asyncio
import dataclasses
import re
import textwrap
from datetime import datetime
from typing import Callable, Coroutine

import httpx
from sqlalchemy import select, text, delete, func, extract
from sqlalchemy.ext.asyncio import AsyncSession

from app import models
from app.config import STATS_APIKEY, logger
from app.stats import utils


class SpamDonorResult:
    def __init__(self,
                 name: str,
                 utm_hits: int,
                 regs: int,
                 prom_link: str,
                 updated_at: datetime,
                 sent_count: int, *args, **kwargs):
        self.name = name
        self.utm_hits = utm_hits
        self.regs = regs
        self.prom_link = prom_link
        self.updated_at = updated_at.strftime('%Y-%m-%d')
        self.sent_count = sent_count
        self.bitly_hits = None


async def get_donors_spam_results(session: AsyncSession) -> list[SpamDonorResult]:
    stmt = text('''
    select donor_name, sum(hits) as utm_hits, sum(registration) as regs, prom_link, updated_at, success_count
    from spam_donors
             join api_stats on donor_name = utm_term
    group by donor_name, prom_link, updated_at, success_count

    ''')
    # time = datetime.now()
    execute = await session.execute(stmt)
    execute_results = [SpamDonorResult(*res) for res in execute.all()]
    await asyncio.gather(*[utils.get_link_summary_for_donor(donor, time_unit='month') for donor in execute_results])
    return execute_results

    # return [
    #     SpamDonorResultsDict(name=donor.donor_name, utm_hits=donor.hits, regs=0, sent_count=donor.success_count)
    #     for donor in donors
    # ]


def __catch_exception(func) -> Callable[[], Coroutine]:
    async def inner(*args, **kwargs) -> list[dict] | None:
        try:
            return await func(*args, **kwargs)
        except httpx.ReadTimeout as error:
            logger.error(f'k0d.info ReadTimeout error occurred {textwrap.wrap(str(error))}')
        except Exception as error:
            logger.error(f'Unexpected exception {type(error).__name__}')

    return inner


@__catch_exception
async def get_stats(period: int = 5) -> list[dict] | None:
    async with httpx.AsyncClient(verify=False) as cli:
        resp = await cli.get(f'https://k0d.info/aff.php?period={period}', headers={'Apikey': STATS_APIKEY})
        if resp.is_success:
            logger.info(f'get_stats {resp.is_success=}')
            try:
                return resp.json()
            except Exception as error:
                logger.error(error)
                return None


async def __get_api_model_items(api_data: list[dict]):
    return [models.ApiDataRow(**api_row) for api_row in api_data]


@dataclasses.dataclass
class RegexIn:
    string: str

    def __eq__(self, other: str) -> bool:
        return bool(re.compile(other).search(self.string))


@dataclasses.dataclass(frozen=True, slots=True)
class RegApiData:
    regs: int
    data: datetime


async def delete_month_api_data(session: AsyncSession) -> None:
    time = datetime.now()
    criteria = extract('month', models.ApiDataRow.date) == time.month
    await session.execute(delete(models.ApiDataRow).where(criteria))
    await session.commit()


async def add_api_data(session: AsyncSession, data_objects: list[models.ApiDataRow]) -> None:
    session.add_all(data_objects)
    await session.commit()


async def get_api_data(session: AsyncSession) -> list[RegApiData]:
    stmt = '''
        select sum(registration) as reg, date from api_stats group by date order by date desc
    '''
    res = await session.execute(text(stmt))
    return [RegApiData(*i) for i in res.all()]


async def get_regs_stat_for_current_month(session: AsyncSession) -> list[models.ApiDataRow]:
    date = datetime.today()
    data_rows_scalars = await session.scalars(
        select(models.ApiDataRow).filter(
            func.date_trunc('month', models.ApiDataRow.date) == func.date_trunc('month', date),
            # func.date_trunc('day', models.ApiDataRow.date) == func.date_trunc('day', date),
            # func.date_trunc('year', models.ApiDataRow.date) == func.date_trunc('year', date),
        )
    )
    return [row for row in data_rows_scalars]


async def get_regs_stat_for_today(session: AsyncSession) -> list[models.ApiDataRow]:
    res = await session.scalars(
        select(models.ApiDataRow)
        .where(models.ApiDataRow.date == func.current_date()).order_by(models.ApiDataRow.hits.desc())
    )
    return [i for i in res]


async def hit_stats(session: AsyncSession) -> list[dict]:
    statement = text('select sum(hits) as hits, utm_term from api_stats group by utm_term order by hits desc')
    res = await session.execute(statement)
    return [{'utm_term': i[1], 'hits': i[0]} for i in res.fetchall()]


async def get_regs_stat_for_specific_date(session: AsyncSession, date: str) -> list[models.ApiDataRow]:
    date = datetime.strptime(date, '%Y-%m-%d')
    res = await session.scalars(
        select(models.ApiDataRow).where(
            func.date_trunc('month', models.ApiDataRow.date) == func.date_trunc('month', date),
            func.date_trunc('day', models.ApiDataRow.date) == func.date_trunc('day', date),
            func.date_trunc('year', models.ApiDataRow.date) == func.date_trunc('year', date)
        )
    )
    return [i for i in res]


async def get_all_donors(session: AsyncSession) -> list[models.SpamDonor]:
    return [spam_donor for spam_donor in await session.scalars(select(models.SpamDonor))]
