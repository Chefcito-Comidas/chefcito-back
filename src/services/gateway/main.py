from typing import Annotated
from fastapi import Body, Depends, FastAPI, Header, Path, Response, status
from pydantic_settings import BaseSettings
from src.model.commons.error import Error
from src.model.gateway import HelloResponse
import requests as r
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from src.model.users.service import HttpUsersProvider
from src.model.users.user_data import UserData, UserToken
from src.model.gateway.users_middleware import AuthMiddleware
from src.model.gateway.service import GatewayService


class Settings(BaseSettings):
    users: str = "http://users"
    auth_url: str = "/users/permissions"
    auth_avoided_urls: list[str] = ["/users"]
    information_prefix: str = "/users"
    dev: bool = True

settings = Settings()
app = FastAPI()

app.add_middleware(AuthMiddleware, 
                   authUrl=f"http://{settings.users}{settings.auth_url}", 
                   avoided_urls=settings.auth_avoided_urls,
                   dev_mode=settings.dev)

security = HTTPBearer()
users = HttpUsersProvider(f"http://{settings.users}")
service = GatewayService(users)

@app.get("/users/health")
async def users_health(_: Annotated[HTTPAuthorizationCredentials, Depends(security)], 
                                              response: Response):
    users_response = r.get(f"http://{settings.users}/health")
    response.status_code = users_response.status_code

@app.get("/users")
async def sign_in(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
                  response: Response) -> UserData | Error:
    return await service.sign_in(credentials, response)

@app.post("/users")
async def sign_up(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
                  user_type: Annotated[str, Body(embed=True, alias='user_type')]) -> UserData | Error:
    
    return await service.sign_up(credentials, user_type) 
