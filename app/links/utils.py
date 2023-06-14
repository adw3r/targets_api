import httpx

from app import config, texts


async def create_link(link_to_short) -> httpx.Response:
    headers = {
        'Authorization': f'Bearer {config.BITLY_KEY}',
    }
    json_data = {
        'long_url': link_to_short,
        'domain': 'bit.ly'
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(url='https://api-ssl.bitly.com/v4/bitlinks', headers=headers, json=json_data)
        return response


async def get_link_summary(bitly_link: str, time_unit: str = 'month') -> dict:
    """

    :param bitly_link: format of bit.ly/3oB8qmJ
    :param time_unit: 'month' 'day'
    :return:
    """
    headers = {
        'Authorization': f'Bearer {config.BITLY_KEY}',
    }
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f'https://api-ssl.bitly.com/v4/bitlinks/{bitly_link}/clicks/summary?unit={time_unit}',
            headers=headers)
        return response.json()


async def get_link_from_bitly(utm_link: str, utm_source: str, utm_campaign: str, utm_term: str) -> httpx.Response:
    project_link = f'{utm_link}&utm_campaign={utm_campaign}&utm_source=' \
                   f'{utm_source}&utm_term={utm_term}#{await texts.generate_text()}'.replace(' ', '+')  # refactor
    params = {
        # "group_guid": "Ba1bc23dE4F",
        "domain": "bit.ly",
        "long_url": project_link
    }
    async with httpx.AsyncClient() as client:
        response = await client.post('https://api-ssl.bitly.com/v4/shorten', json=params,
                                     headers={'Authorization': f'Bearer {config.BITLY_KEY}'})
    return response
