from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import schemas, models, database

router = APIRouter(
    prefix='/texts',
    tags=['Texts']
)


@router.get('')
async def get_texts(db_session: AsyncSession = Depends(database.create_async_session)):
    results = await db_session.scalars(select(models.Text))
    return results.all()


@router.put('')
async def get_texts(text: schemas.TextSchema, db_session: AsyncSession = Depends(database.create_async_session)):
    models_text = models.Text(**text.dict())
    db_session.add(models_text)
    await db_session.commit()
    return models_text
