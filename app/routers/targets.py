from fastapi import APIRouter, Depends, Response, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app import models, database, cache, service

router = APIRouter(
    prefix='/targets',
    tags=['Targets api']
)


@router.get('')
async def get_factories(method: str = 'info', db_session: AsyncSession = Depends(database.create_async_session)):
    match method:
        case 'info':
            res = await service.get_available_sources_join_texts(db_session)
            return res


@router.get('/{pool}')
async def get_factory_pool(pool: str, method: str = 'info',
                           db_session: AsyncSession = Depends(database.create_async_session)):
    source: models.Source = await service.get_source_by_name(db_session, source_name=pool)
    if not source:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'source with name {pool} not found!')
    match method:
        case 'info':
            return source
        case 'pop':
            target = cache.redis_cli.lpop(pool)
            if not target:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response(content=target)
