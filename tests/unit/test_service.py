import pytest

from app.stats.service import get_stats


@pytest.mark.asyncio
async def test_get_stats():
    results = sorted(await get_stats(6), key=lambda d: d['date'], reverse=True)
    print(results)
