from app import models, database
from app.stats import service


async def update_api_data() -> None:
    month_stats: list[dict] | None = await service.get_stats()
    if not month_stats:
        return
    data_objects: list[models.ApiDataRow] = await service.__get_api_model_items(month_stats)
    async with database.context_async_session() as session:
        await service.delete_month_api_data(session)
        await service.add_api_data(session, data_objects)
