from pathlib import Path

import aiofiles
from fastapi import APIRouter, Depends, Response, HTTPException, File, UploadFile, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app import models, database, cache, service, config, utils

router = APIRouter(
    prefix='/targets',
    tags=['Targets']
)


@router.post('/files')
async def upload_file(tasks: BackgroundTasks, source_name=File(...), lang=File(...), file: UploadFile = File(...)):
    path = Path(config.TARGETS_FOLDER, file.filename)
    async with aiofiles.open(path, 'wb') as f:
        await f.write(await file.read())
    tasks.add_task(utils.add_targets_to_db, source_name, lang, path)
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
            target = cache.redis_cli.lpop(pool)
            if not target:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return Response(content=target)
