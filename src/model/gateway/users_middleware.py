from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint, DispatchFunction
from starlette.requests import Request
from starlette.responses import Response
from fastapi import status
from starlette.types import ASGIApp
import asyncio
import aiohttp

from src.model.users.user_data import UserToken 

class AuthMiddleware(BaseHTTPMiddleware):
    
    def __init__(self, app: ASGIApp, authUrl: str, dispatch: DispatchFunction | None = None) -> None:
        super().__init__(app, dispatch)
        self.authUrl = authUrl

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        token = request.headers.get('Authorization', None)
        if token:
            token = self.__parse_token(token)
            session = aiohttp.ClientSession()
            response = await session.post(self.authUrl, json=UserToken(id_token=token).model_dump())
            print(f"response status: {response.status}")
        return await call_next(request)

    def __parse_token(self, token: str) -> str:
        return token.lstrip('Bearer').lstrip(" ")
    
    def __not_authorized(self) -> Response:
        response = Response()
        response.status_code = status.HTTP_403_FORBIDDEN
        return response
            
