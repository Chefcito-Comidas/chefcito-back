from starlette.datastructures import MutableHeaders
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint, DispatchFunction
from starlette.requests import Request
from starlette.responses import Response
from fastapi import status
from starlette.types import ASGIApp
import asyncio
import aiohttp

from src.model.commons.caller import post, recover_json_data
from src.model.users.auth_request import AuthRequest
from src.model.users.user_data import UserToken 

class AuthMiddleware(BaseHTTPMiddleware):
    
    def __init__(self, app: ASGIApp, 
                 authUrl: str, 
                 avoided_urls: list[str],
                 dispatch: DispatchFunction | None = None) -> None:
        super().__init__(app, dispatch)
        self.authUrl = authUrl
        self.avoided = avoided_urls

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        if not request.url.path in self.avoided:
            request, token = self.__modify_headers(request) 
            response = await self.__auth_call(token, request.url.path)
            return await self.__call_if_authorized(request, response, call_next) 
        return await call_next(request)

    def __parse_token(self, token: str) -> str:
        return token.lstrip('Bearer').lstrip(" ")
    
    def __modify_headers(self, request: Request) -> tuple[Request, str]:
        token = request.headers.get('Authorization', None)
        if token:
            return request, token
        headers = MutableHeaders(request._headers)
        # TODO: Fix this hardcoded values
        headers.append('Authorization', 'Bearer anonymous')
        request._headers = headers
        return request, 'Bearer anonymous'
    
    async def __call_if_authorized(self, request: Request, auth_response: aiohttp.ClientResponse, call_next: RequestResponseEndpoint) -> Response:
        if auth_response.status == status.HTTP_200_OK:
            result = await call_next(request)
        else: result =  self.__not_authorized()
        auth_response.close()
        return result
    
    async def __auth_call(self, token: str, endpoint: str) -> aiohttp.ClientResponse:
        token = self.__parse_token(token)
        body = AuthRequest(id_token=token, endpoint=endpoint).model_dump()
        response = await post(self.authUrl, body=body)
        return response 

    def __not_authorized(self) -> Response:
        response = Response()
        response.status_code = status.HTTP_403_FORBIDDEN
        return response
            
