import asyncio

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import utils, models, database
from app.config import logger

router = APIRouter(
    prefix='/stats',
    tags=['Stats']
)


@router.get('')
async def get_stats(db_session: AsyncSession = Depends(database.create_async_session)):
    all_spam_donors = await db_session.scalars(select(models.SpamDonor))
    logger.info(all_spam_donors.all())
    results = await asyncio.gather(*[asyncio.create_task(utils.get_link_summary(donor.prom_link)) for donor in
                                     all_spam_donors.all()])
    __message = [result.json() for result in results]
    return all_spam_donors.all()
