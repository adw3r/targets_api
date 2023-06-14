from fastapi import APIRouter, Depends, Response, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app import models, database, schemas

router = APIRouter(
    prefix='/projects',
    tags=['Donors']
)


@router.post('')
async def create_project(donor_scheme: schemas.SpamDonorPostSchema,
                         db_session: AsyncSession = Depends(database.create_async_session)):
    donor_instance = await db_session.scalar(
        select(models.SpamDonor).where(models.SpamDonor.donor_name == donor_scheme.donor_name))
    if donor_instance:
        donor_instance.update(**donor_scheme.dict())
        db_session.add(donor_instance)
        await db_session.commit()
        return donor_instance
    else:
        donor_instance = models.SpamDonor(**donor_scheme.dict())
        db_session.add(donor_instance)
        await db_session.commit()
        return donor_instance


@router.get('/{project_name}')
async def get_project_status(project_name: str, db_session: AsyncSession = Depends(database.create_async_session)):
    res = await db_session.scalar(select(models.SpamDonor).where(models.SpamDonor.donor_name == project_name))
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Donor with name {} not found'.format(project_name))
    return res


@router.put('/{project_name}')
async def send_count(project_name: str, json_form: schemas.SpamDonorCount,
                     db_session: AsyncSession = Depends(database.create_async_session)):
    donor_instance = await db_session.scalar(
        select(models.SpamDonor).where(models.SpamDonor.donor_name == project_name))
    if not donor_instance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'donor {project_name} was not found!')
    if json_form.success_count >= 0:
        donor_instance.success_count += json_form.success_count
    else:
        donor_instance.fail_count += json_form.success_count
    if donor_instance.fail_count <= -200:
        donor_instance.status = False
    db_session.add(donor_instance)
    await db_session.commit()
    return Response(content='success')