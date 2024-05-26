"""
Caller provides a simple interface to manage aihttp calls
"""


import aiohttp


async def get(url: str, body: dict = {}, data: dict = {}, params: dict = {}) -> aiohttp.ClientResponse:
    client = aiohttp.ClientSession()
    return await client.get(url, body=body, data=data, params=params)

async def post(url: str, body: dict = {}, data: dict = {}, params: dict = {}) -> aiohttp.ClientResponse:
    client = aiohttp.ClientSession()
    return await client.post(url, body=body, data=data, params=params)
