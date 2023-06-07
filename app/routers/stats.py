import asyncio

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app import utils, models, database, service
from app.config import logger

router = APIRouter(
    prefix='/stats',
    tags=['Stats']
)


@router.get('/clicks')
async def get_stats(time_unit: str = 'month', db_session: AsyncSession = Depends(database.create_async_session)):
    links: list[models.Bitly] = await service.get_all_links(db_session)
    results = await asyncio.gather(
        *[asyncio.create_task(utils.get_link_summary(bitly.link_id, time_unit)) for bitly in links]
    )
    return results


@router.get('/regs')
async def get_regs_stat(time_format: str = 'all', db_session: AsyncSession = Depends(database.create_async_session)):
    match utils.regex_in(time_format):
        case r'\d{4}-\d{2}-\d{2}':
            results = await service.get_regs_stat_for_specific_date(db_session, time_format)
            return results
        case r'today':
            res = await service.get_regs_stat_for_today(db_session)
            return res
        case r'month':
            results = await service.get_regs_stat_for_current_month(db_session)
            return results
        case 'all':
            res = await service.get_api_data(db_session)
            logger.debug(f'{len(res)}')
            return res
