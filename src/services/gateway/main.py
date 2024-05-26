from typing import Annotated
from fastapi import Body, Depends, FastAPI, Path, Response
from pydantic_settings import BaseSettings
from src.model.gateway import HelloResponse
import requests as r
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from src.model.users.auth_request import AuthRequest
from src.model.users.user_data import UserData
from src.model.gateway.users_middleware import AuthMiddleware

class Settings(BaseSettings):
    auth_url: str = "http://users/users"
    auth_avoided_urls: list[str] = ["/docs", "/openapi.json"]

settings = Settings()
app = FastAPI()

app.add_middleware(AuthMiddleware, authUrl=settings.auth_url, avoided_urls=settings.auth_avoided_urls)

security = HTTPBearer()

# TODO:Add credentials to all endpoints 
@app.get("/{name}")
async def hello(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)], name: Annotated[str, Path()]) -> HelloResponse:
    return HelloResponse(name=f"Hello, {name}") 

@app.get("/dummy")
async def dummy():
    return HelloResponse(name="Hello, Dummy")

@app.get("/users/health")
async def users_health(response: Response):
    users_response = r.get("http://users/health")
    response.status_code = users_response.status_code

@app.post("/users")
async def get_data(request: Annotated[AuthRequest, Body()]) -> UserData:
    users_response = r.post("http://users/users", data=request.model_dump_json())
    
    return users_response.json()
    
