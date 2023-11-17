from fastapi import APIRouter, Depends, Response, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app import models, database, schemas, service, config, donors

router = APIRouter(
    prefix='/donors',
    tags=['Donors']
)


@router.get('/')
async def get_donors(db_session: AsyncSession = Depends(database.create_async_session)):
    results = await donors.service.get_all_donors(db_session)
    return results


@router.post('/')
async def create_project(donor_scheme: schemas.SpamDonorPostSchema,
                         db_session: AsyncSession = Depends(database.create_async_session)):
    donor_instance: models.SpamDonor = await service.get_donor_by_name(db_session, donor_scheme.donor_name)
    if donor_instance:
        donor_instance.update(**donor_scheme.model_dump())
        db_session.add(donor_instance)
        await db_session.commit()
    else:
        donor_instance = models.SpamDonor(**donor_scheme.model_dump())
        db_session.add(donor_instance)
        await db_session.commit()
    await db_session.refresh(donor_instance)
    return donor_instance


@router.get('/{donor_name}')
async def get_project_info(donor_name: str, db_session: AsyncSession = Depends(database.create_async_session)):
    donor_instance: models.SpamDonor = await service.get_donor_by_name(db_session, donor_name)
    if not donor_instance:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Donor with name {} not found'.format(donor_name))
    if donor_instance.fail_count >= config.FAILS_LIMIT and donor_instance.status is True:
        donor_instance.status = False
        db_session.add(donor_instance)
        await db_session.commit()
        await db_session.refresh(donor_instance)
    return donor_instance


@router.patch('/{donor_name}/status')
async def update_status(donor_name: str, status: bool,
                        db_session: AsyncSession = Depends(database.create_async_session)):
    if donor_name == 'all':
        donors = await service.get_donors_with_false_status(session=db_session)
        for donor in donors:
            donor.status = status
            donor.fail_count = 0
            db_session.add(donor)
            await db_session.commit()
            await db_session.refresh(donor)
        return donors
    else:
        donor_instance: models.SpamDonor = await service.get_donor_by_name(db_session, donor_name)
        if not donor_instance:
            raise HTTPException(detail=f'donor {donor_name} was not found!', status_code=404)
        donor_instance.status = status
        if status:
            donor_instance.fail_count = 0
        else:
            donor_instance.fail_count = 300
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
    if json_form.success_count > 0:
        donor_instance.success_count += json_form.success_count
        donor_instance.fail_count = 0
        donor_instance.status = True
    elif json_form.success_count == 0:
        pass
    else:
        donor_instance.fail_count += abs(json_form.success_count)
        if donor_instance.fail_count >= config.FAILS_LIMIT:
            donor_instance.status = False
    db_session.add(donor_instance)
    await db_session.commit()
    await db_session.refresh(donor_instance)
    return Response(content='success')
