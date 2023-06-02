import asyncio
import multiprocessing

import uvicorn
from fastapi import FastAPI, Response, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import RedirectResponse

from app import database, service, models, schemas, utils, cache
from app.config import HOST, PORT, DEBUG, logger

app = FastAPI()
active_target_pools = {}


def create_cache():
    logger.info('creating cache...')
    multiprocessing.Process(target=cache.check_that_cache_is_not_empty).start()


@app.on_event('startup')
def startup():
    create_cache()


@app.get('/')
async def get_root():
    return RedirectResponse('/docs')


@app.get('/targets')
async def get_factories(method: str = 'info', db_session: AsyncSession = Depends(database.create_async_session)):
    match method:
        case 'info':
            res = await service.get_available_sources_join_texts(db_session)
            return res


@app.get('/targets/{pool}')
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


@app.get('/texts')
async def get_texts(db_session: AsyncSession = Depends(database.create_async_session)):
    results = await db_session.scalars(select(models.Text))
    return results.all()


@app.put('/texts')
async def get_texts(text: schemas.TextSchema, db_session: AsyncSession = Depends(database.create_async_session)):
    models_text = models.Text(**text.dict())
    db_session.add(models_text)
    await db_session.commit()
    return models_text


@app.get('/bitly/donors')
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


@app.post('/bitly/link')
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


@app.get('/bitly/link/summary')
async def get_link_summary(link_id, db_session: AsyncSession = Depends(database.create_async_session)):
    result = await utils.get_link_summary(link_id)
    bitly_instance = await db_session.scalar(select(models.Bitly).where(models.Bitly.link_id == link_id))
    result_json = result.json()
    result_json.update(bitly_instance.to_dict())
    return result_json


@app.get('/bitly/all')
async def get_all_bitly_links(db_session: AsyncSession = Depends(database.create_async_session)):
    result = await db_session.scalars(select(models.Bitly))
    return result.all()


@app.get('/referrals', response_model=list[schemas.ReferralSchema])
async def referral_method(db_session: AsyncSession = Depends(database.create_async_session)
                          ) -> list[schemas.ReferralSchema]:
    referral_models: list[models.Referral] = await service.get_referrals_with_where(db_session)
    return [schemas.ReferralSchema(**ref.as_dict()) for ref in referral_models]


@app.post('/projects/')
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


@app.get('/projects/{project_name}')
async def get_project_status(project_name: str, db_session: AsyncSession = Depends(database.create_async_session)):
    res = await db_session.scalar(select(models.SpamDonor).where(models.SpamDonor.donor_name == project_name))
    if not res:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail='Donor with name {} not found'.format(project_name))
    return res


@app.put('/projects/{project_name}')
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


@app.get('/stats')
async def get_stats(db_session: AsyncSession = Depends(database.create_async_session)):
    all_spam_donors = await db_session.scalars(select(models.SpamDonor))
    results = await asyncio.gather(*[asyncio.create_task(utils.get_link_summary(donor.prom_link)) for donor in
                                     all_spam_donors.all()])
    __message = [result.json() for result in results]
    return __message


if __name__ == '__main__':
    uvicorn.run('main:app', host=HOST, port=int(PORT), reload=DEBUG)
