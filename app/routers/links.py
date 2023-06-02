from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app import models, database, service, utils
from app.config import logger

router = APIRouter(
    prefix='/bitly',
    tags=['Bitly']
)


@router.get('/donors')
async def get_shortened_link_v2(
        project_name: str,
        targets_base: str,
        donor: str,
        db_session: AsyncSession = Depends(database.create_async_session)):
    project_name = project_name.lower()
    referral: models.Referral = await service.get_referral_with_name(db_session, project_name)
    if not referral:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'Referral {project_name} is not found')
    result = await utils.get_link_from_bitly(utm_source=targets_base, utm_campaign=referral.name, utm_term=donor,
                                             utm_link=referral.link)
    result_json = result.json()
    db_session.add(
        models.Bitly(link_id=result_json['id'],
                     long_url=result_json['long_url'],
                     created_at=result_json['created_at'],
                     link=result_json['link']
                     ))
    await db_session.commit()
    return result.json()


@router.post('/link')
async def create_link_straight(link, db_session: AsyncSession = Depends(database.create_async_session)):
    result = await utils.create_link(link)
    result_json = result.json()
    if 'errors' in result_json.keys():
        logger.info(result_json)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail={'result': result_json})
    instance = models.Bitly(link_id=result_json['id'],
                            long_url=result_json['long_url'],
                            created_at=result_json['created_at'],
                            link=result_json['link'])
    db_session.add(instance)
    await db_session.commit()
    return result_json


@router.get('/link/summary')
async def get_link_summary(link_id, db_session: AsyncSession = Depends(database.create_async_session)):
    result = await utils.get_link_summary(link_id)
    bitly_instance = await db_session.scalar(select(models.Bitly).where(models.Bitly.link_id == link_id))
    result_json = result.json()
    result_json.update(bitly_instance.to_dict())
    return result_json


@router.get('/all')
async def get_all_bitly_links(db_session: AsyncSession = Depends(database.create_async_session)):
    result = await db_session.scalars(select(models.Bitly))
    return result.all()
