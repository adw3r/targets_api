import pytest

import httpx

from app import config, links


@pytest.mark.asyncio
async def test_get_link_summary():
    link_id = 'bit.ly/48rdBru'

    res = await links.get_link_summary(link_id)
    assert res.json().get('units') is not None


def test_get_bitly_stats():
    link_id = 'bit.ly/48rdBru'
    params = {
        'link_id': link_id
    }
    resp = httpx.get(f'http://localhost:{config.PORT}/bitly/link/summary', params=params)
    print(resp.text)
    assert resp.json().get('units') is not None


def test_set_status_for_all_donors():
    params = {
        'status': 'true',
    }

    response = httpx.patch('http://127.0.0.1:8181/donors/test/status', params=params)
    print(response.text)
