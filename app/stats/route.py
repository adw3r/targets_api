import asyncio

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app import models, database, service, links
from . import utils
from app.config import logger

router = APIRouter(
    prefix='/stats',
    tags=['Stats']
)


@router.get('/donors')
async def donors_stats(db_session: AsyncSession = Depends(database.create_async_session)):
    statement = text('''
        select donor_name, success_count, fail_count from spam_donors
    ''')
    res = await db_session.execute(statement)
    return [{'donor_name': row[0], 'success_count': row[1], 'fail_count': row[2]} for row in res.fetchall()]


@router.get('/clicks')
async def get_stats(time_unit: str = 'month', db_session: AsyncSession = Depends(database.create_async_session)):
    links_list: list[models.Bitly] = await service.get_all_links(db_session)
    results = await asyncio.gather(
        *[asyncio.create_task(links.get_link_summary(bitly.link_id, time_unit)) for bitly in links_list]
    )
    return results


@router.get('/hits')
async def get_hits(db_session: AsyncSession = Depends(database.create_async_session)):
    results: dict = await service.hit_stats(db_session)
    return results


@router.get('/regs')
async def get_regs_stat(time_format: str = 'all', db_session: AsyncSession = Depends(database.create_async_session)):
    match utils.RegexIn(time_format):
        case r'\d{4}-\d{2}-\d{2}':
            results = await service.get_regs_stat_for_specific_date(db_session, time_format)
            return results
        case 'today':
            res = await service.get_regs_stat_for_today(db_session)
            return res
        case 'month':
            results = await service.get_regs_stat_for_current_month(db_session)
            return results
        case 'all':
            res: list[service.RegApiData] = await service.get_api_data(db_session)
            logger.debug(f'{len(res)}')
            return res
