import datetime

import pytest

from app import service, database, models
from app.config import logger


@pytest.fixture
def db_session():
    return database.create_async_session()


@pytest.mark.asyncio
async def test_get_source_info_by_name(db_session):
    db_session = await anext(db_session)
    test_info = await service.get_source_info_by_name(session=db_session, source_name='alotof')
    print(test_info)
    await db_session.close()


@pytest.mark.asyncio
async def test_get_source(db_session):
    db_session = await anext(db_session)
    source: models.Source = await service.get_source_by_name(db_session, 'alotof')
    print(source)
    assert type(source) == models.Source
    await db_session.close()


@pytest.mark.asyncio
async def test_get_target(db_session):
    db_session = await anext(db_session)
    source: models.Source = await service.get_source_by_name(db_session, 'ukgoo')
    targets = await service.get_one_not_spammed_target_with_update(db_session, source, limit=10_000)
    print(targets)
    for t in targets:
        assert type(t) == models.TargetEmail
    await db_session.close()


@pytest.mark.asyncio
async def test_get_referrals_with_where(db_session):
    db_session = await anext(db_session)
    res: list[models.Referral] = await service.get_referrals_with_where(db_session)
    assert type(res[0]) == models.Referral
    await db_session.close()


@pytest.mark.asyncio
async def test_get_referral_with_name(db_session):
    db_session = await anext(db_session)
    res: list[models.Referral] = await service.get_referrals_with_where(db_session)
    res = await service.get_referral_with_name(db_session, res[0].name)
    assert type(res) == models.Referral
    await db_session.close()


@pytest.mark.asyncio
async def test_false_get_referral_with_name(db_session):
    db_session = await anext(db_session)
    ref_name = 'test'
    res: models.Referral | None = await service.get_referral_with_name(db_session, ref_name)
    assert res is None
    await db_session.close()


@pytest.mark.asyncio
async def test_get_all_sources_info(db_session):
    db_session = await anext(db_session)
    results = await service.get_all_sources_info(db_session)
    print(results)
    await db_session.close()


@pytest.mark.asyncio
async def test_get_stats_for_today(db_session):
    db_session = await anext(db_session)

    results = await service.get_regs_stat_for_today(db_session)
    time_format = '%Y-%m-%d'
    row_date = results[0].date.strftime(time_format)
    logger.debug(row_date)
    assert row_date == datetime.datetime.today().strftime(time_format)
    assert results is not None
    await db_session.close()


@pytest.mark.asyncio
async def test_get_stats_for_month(db_session):
    '''2023-07-04 00:00:00.000000'''
    time_format = '%Y-%m-%d'

    db_session = await anext(db_session)
    results = await service.get_regs_stat_for_current_month(db_session)
    result = results[0]
    logger.debug(result)
    assert results is not None
    assert result.date.month == datetime.datetime.today().month

    await db_session.close()
