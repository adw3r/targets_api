import pytest

from app import donors, database, models


@pytest.mark.asyncio
async def test_get_donors_spam_results():
    async with database.context_async_session() as db_session:
        results: list[models.SpamDonor] = await donors.service.get_all_donors(session=db_session)
        print(results)
        assert type(results) is list
        for item in results:
            assert type(item) is models.SpamDonor
