import pytest

from app import models, database, stats


@pytest.mark.asyncio
async def test_retrieve_api_data_into_database():
    api_data: list[dict] = await stats.service.get_stats()
    data_objects: list[models.ApiDataRow] = await stats.service.get_api_model_items(api_data)
    for row in data_objects:
        assert type(row) is models.ApiDataRow


@pytest.mark.asyncio
async def test_add_api_data_to_db():
    await stats.utils.update_api_data()
    async with database.context_async_session() as session:
        results: list[stats.service.RegApiData] = await stats.service.get_api_data(session)
    assert results is not None


@pytest.mark.asyncio
async def test_delete_month_api_data():
    async with database.context_async_session() as session:
        await stats.service.delete_month_api_data(session)
