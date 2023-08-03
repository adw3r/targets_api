from app import models, database, links
from app.stats import service


async def update_api_data() -> None:
    month_stats: list[dict] | None = await service.get_stats()
    if not month_stats:
        return
    data_objects: list[models.ApiDataRow] = await service.__get_api_model_items(month_stats)
    async with database.context_async_session() as session:
        await service.delete_month_api_data(session)
        await service.add_api_data(session, data_objects)


async def get_link_summary_for_donor(donor: models.SpamDonor | service.SpamDonorResult,
                                     **kwargs) -> models.SpamDonor:
    bitly_link = donor.prom_link
    response = await links.utils.get_link_summary(bitly_link, **kwargs)
    donor.bitly_hits = response.json().get('total_clicks')
    return donor
