"""
Caller provides a simple interface to manage aihttp calls
"""


from typing import Any
import aiohttp
import asyncio


async def __call(method, url: str, body: dict, headers: dict, params: dict) -> aiohttp.ClientResponse:
    client = aiohttp.ClientSession()
    response = await method(client, url, json=body, headers=headers,  params=params)
    await client.close()
    return response

async def recover_json_data(response: aiohttp.ClientResponse) -> Any:
    data = await asyncio.wait_for(response.json(), 0.5)
    response.close()
    return data

async def get(url: str, body: dict = {}, data: dict = {}, params: dict = {}) -> aiohttp.ClientResponse:  
    return await __call(aiohttp.ClientSession.get, url, body, data, params) 

async def put(url: str, body: dict = {}, data: dict = {}, params: dict = {}) -> aiohttp.ClientResponse:
    return await __call(aiohttp.ClientSession.put, url, body, data, params)

async def delete(url: str, body: dict = {}, data: dict = {}, params: dict = {}) -> aiohttp.ClientResponse:
    return await __call(aiohttp.ClientSession.delete, url, body, data, params)

async def post(url: str, body: dict = {}, data: dict = {}, params: dict = {}) -> aiohttp.ClientResponse:
   return await __call(aiohttp.ClientSession.post, url, body, data, params) 
