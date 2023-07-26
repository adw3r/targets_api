from fastapi import APIRouter, Depends, Response, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app import models, database, schemas, service

router = APIRouter(
    prefix='/donors',
    tags=['Donors']
)


@router.get('/{donor_name}')
async def get_project_info(donor_name: str, db_session: AsyncSession = Depends(database.create_async_session)):
    donor: models.SpamDonor = await service.get_donor_by_name(db_session, donor_name)
    if not donor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Donor with name {} not found'.format(donor_name))
    if donor.fail_count <= -200 and donor.status is True:
        donor.status = False
        db_session.add(donor)
        await db_session.commit()
        await db_session.refresh(donor)
    return donor


@router.post('')
async def create_project(donor_scheme: schemas.SpamDonorPostSchema,
                         db_session: AsyncSession = Depends(database.create_async_session)):
    donor_instance: models.SpamDonor = await service.get_donor_by_name(db_session, donor_scheme.donor_name)
    if donor_instance:
        donor_instance.update(**donor_scheme.dict())
        db_session.add(donor_instance)
        await db_session.commit()
    else:
        donor_instance = models.SpamDonor(**donor_scheme.dict())
        db_session.add(donor_instance)
        await db_session.commit()
    await db_session.refresh(donor_instance)
    return donor_instance


@router.patch('/{donor_name}/status')
async def update_status(donor_name: str, status: bool,
                        db_session: AsyncSession = Depends(database.create_async_session)):
    donor_instance: models.SpamDonor = await service.get_donor_by_name(db_session, donor_name)
    donor_instance.status = status
    donor_instance.fail_count = 0
    db_session.add(donor_instance)
    await db_session.commit()
    await db_session.refresh(donor_instance)
    return donor_instance


@router.patch('/{donor_name}/counters')
async def send_count(donor_name: str, json_form: schemas.SpamDonorCount,
                     db_session: AsyncSession = Depends(database.create_async_session)):
    donor_instance = await service.get_donor_by_name(db_session, donor_name)
    if not donor_instance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'donor {donor_name} was not found!')
    if json_form.success_count >= 0:
        donor_instance.success_count += json_form.success_count
    else:
        donor_instance.fail_count += json_form.success_count
    db_session.add(donor_instance)
    await db_session.commit()
    return Response(content='success')
