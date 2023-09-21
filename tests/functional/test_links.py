import httpx

from app import config


def test_get_bitly_stats():
    link_id = 'bit.ly/48rdBru'
    params = {
        'link_id': link_id
    }
    resp = httpx.get(f'http://localhost:{config.PORT}/bitly/link/summary', params=params)
    print(resp.text)
