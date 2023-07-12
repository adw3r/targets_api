from app import models, database
from app.config import logger
from app.stats import service


async def update_api_data():
    month_stats: list[dict] = await service.get_stats()

    data_objects: list[models.ApiDataRow] = await service.get_api_model_items(month_stats)
    logger.info(f'{data_objects[0]=}')
    async with database.context_async_session() as session:
        await service.delete_month_api_data(session)
        await service.add_api_data(session, data_objects)
