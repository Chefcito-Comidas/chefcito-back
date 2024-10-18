"""
Caller provides a simple interface to manage aihttp calls
"""
from typing import Any, Awaitable, Callable
import aiohttp
import asyncio

from fastapi import status


type HTTPMethod = Callable[..., Awaitable[aiohttp.ClientResponse]]

async def __call(method: HTTPMethod, url: str, body: dict, headers: dict, params: dict) -> aiohttp.ClientResponse:
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

async def with_retry(method: HTTPMethod, url: str, body: dict = {}, data: dict = {}, params: dict = {}) -> Any:
    max_tries = 3
    count = 0
    while count < max_tries:
        try:
            response = await method(url, body=body, data=data, params=params)
            if response.status != status.HTTP_200_OK:
                count += 1
            else:
                return response
        except Exception:
            count += 1
    raise Exception("Failed retry")

async def back_off(method: HTTPMethod, url: str, body: dict = {}, data: dict = {}, params: dict = {}) -> Any:
    wait_time = 0.5
    while wait_time <= 4:
        response = None
        try:
            response = await method(url, body=body, data=data, params=params)
            returnable_data = await asyncio.wait_for(response.json(), wait_time)
            response.close()
            return returnable_data
        except TimeoutError:
            if response is not None:
                response.close()
            wait_time *= 2

    raise Exception("Failed to connect to firebase server")
