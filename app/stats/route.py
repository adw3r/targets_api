import asyncio

from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import database, models
from app import links
from app.config import logger
from app.stats import service

router = APIRouter(
    prefix='/stats',
    tags=['Stats']
)


@router.get('')
async def root_stats():
    return RedirectResponse('/stats/regs')


@router.get('/donors')
async def donors_stats(db_session: AsyncSession = Depends(database.create_async_session)):
    spam_donors: list[models.SpamDonor] = await service.get_all_donors(db_session)
    return spam_donors


@router.get('/all')
async def get_all_api_stats(db_session: AsyncSession = Depends(database.create_async_session)):
    results: list[models.ApiDataRow] = [
        i for i in
        await db_session.scalars(select(models.ApiDataRow).order_by(models.ApiDataRow.registration.desc()))
    ]
    return results


@router.get('/clicks')
async def get_stats(time_unit: str = 'month',
                    db_session: AsyncSession = Depends(database.create_async_session)):  # todo
    spam_donors: list[models.SpamDonor] = await service.get_all_donors(db_session)
    await asyncio.gather(*[links.get_link_summary(donor, time_unit) for donor in spam_donors])
    return spam_donors


@router.get('/hits')
async def get_hits(db_session: AsyncSession = Depends(database.create_async_session)):
    results: list[dict] = await service.hit_stats(db_session)
    return results


@router.get('/regs')
async def get_regs_stat(time_format: str = 'all', db_session: AsyncSession = Depends(database.create_async_session)):
    match service.RegexIn(time_format):
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
