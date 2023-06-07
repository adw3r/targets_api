import pytest

from app import utils


@pytest.mark.asyncio
async def test_get_stats():
    result = await utils.get_stats()
    print(result)
    assert type(result) is list
