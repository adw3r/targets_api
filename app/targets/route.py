import redis.asyncio
from fastapi import APIRouter, Depends, Response, HTTPException, File, UploadFile, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app import models, database, service
from app.config import REDIS_PASSWORD, REDIS_PORT, REDIS_HOST
from . import utils

redis_cli = redis.asyncio.Redis(password=REDIS_PASSWORD, port=REDIS_PORT, host=REDIS_HOST, max_connections=10000)

router = APIRouter(prefix='/targets', tags=['Targets'])


class FileProperties(BaseModel):
    source_name: str
    lang: str


@router.post('/files')
async def upload_file(tasks: BackgroundTasks, properties: FileProperties = Depends(), file: UploadFile = File(...)):
    path = await utils.write_file(file)
    tasks.add_task(utils.add_targets_to_db, properties.source_name, properties.lang, path)
    return True


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
            target = await redis_cli.lpop(pool)
            if not target:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
            return Response(content=target)
