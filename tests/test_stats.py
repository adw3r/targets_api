import pytest

from app import utils, models, database, service


@pytest.mark.asyncio
async def test_retrieve_api_data_into_database():
    api_data: list[dict] = await utils.get_stats()
    data_objects: list[models.ApiDataRow] = await utils.get_api_model_items(api_data)
    for row in data_objects:
        assert type(row) is models.ApiDataRow


@pytest.mark.asyncio
async def test_add_api_data_to_db():
    api_data: list[dict] = await utils.get_stats()
    data_objects: list[models.ApiDataRow] = await utils.get_api_model_items(api_data)
    async with database.context_async_session() as session:
        await service.delete_api_data(session)
        await service.add_api_data(session, data_objects)
        results = await service.get_api_data(session)
    assert results is not None
