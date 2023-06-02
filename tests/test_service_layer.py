import pytest

from app import service, database, models


@pytest.fixture
def db_session():
    return database.create_async_session()


def session():
    return database.create_sync_session()


@pytest.mark.asyncio
async def test_get_source_info_by_name(db_session):
    db_session = await anext(db_session)
    test_info = await service.get_source_info_by_name(session=db_session, source_name='alotof')
    print(test_info)


@pytest.mark.asyncio
async def test_get_source(db_session):
    db_session = await anext(db_session)
    source: models.Source = await service.get_source_by_name(db_session, 'alotof')
    print(source)
    assert type(source) == models.Source


@pytest.mark.asyncio
async def test_get_target(db_session):
    db_session = await anext(db_session)
    source: models.Source = await service.get_source_by_name(db_session, 'ukgoo')
    targets = await service.get_one_not_spammed_target_with_update(db_session, source, limit=10_000)
    print(targets)
    for t in targets:
        assert type(t) == models.TargetEmail


@pytest.mark.asyncio
async def test_get_referrals_with_where(db_session):
    db_session = await anext(db_session)
    res: list[models.Referral] = await service.get_referrals_with_where(db_session)
    assert type(res[0]) == models.Referral


@pytest.mark.asyncio
async def test_get_referral_with_name(db_session):
    db_session = await anext(db_session)
    res: list[models.Referral] = await service.get_referrals_with_where(db_session)
    res = await service.get_referral_with_name(db_session, res[0].name)
    assert type(res) == models.Referral


@pytest.mark.asyncio
async def test_false_get_referral_with_name(db_session):
    db_session = await anext(db_session)
    ref_name = 'test'
    res: models.Referral | None = await service.get_referral_with_name(db_session, ref_name)
    assert res is None


@pytest.mark.asyncio
async def test_get_all_sources_info(db_session):
    db_session = await anext(db_session)
    results = await service.get_all_sources_info(db_session)
    print(results)
