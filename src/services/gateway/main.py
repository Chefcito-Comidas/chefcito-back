from typing import Annotated
from fastapi import Body, Depends, FastAPI, Header, Path, Response, status
from pydantic_settings import BaseSettings
from src.model.commons.caller import get, post, recover_json_data
from src.model.commons.error import Error
from src.model.gateway import HelloResponse
import requests as r
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from src.model.users.auth_request import AuthRequest
from src.model.users.user_data import UserData, UserToken
from src.model.gateway.users_middleware import AuthMiddleware

class Settings(BaseSettings):
    auth_url: str = "http://users/users/permissions"
    auth_avoided_urls: list[str] = ["/users"]
    information_prefix: str = "/users"

settings = Settings()
app = FastAPI()

app.add_middleware(AuthMiddleware, 
                   authUrl=settings.auth_url, 
                   avoided_urls=settings.auth_avoided_urls)

security = HTTPBearer()

# TODO: remove all logic from this file and make it testable
@app.get("/{name}")
async def hello(_: Annotated[HTTPAuthorizationCredentials, Depends(security)], name: Annotated[str, Path()]) -> HelloResponse:
    return HelloResponse(name=f"Hello, {name}") 


@app.get("/users/health")
async def users_health(_: Annotated[HTTPAuthorizationCredentials, Depends(security)], 
                                              response: Response):
    users_response = r.get("http://users/health")
    response.status_code = users_response.status_code

@app.get("/users")
async def sign_in(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
                  response: Response) -> UserData | Error:
    """
    Gets data from the respective user
    """
    try:
        data = UserToken(id_token=credentials.credentials)
        users_response = await post("http://users/users", body=data.model_dump())
        return await recover_json_data(users_response) 
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return Error.from_exception(e, "/users")


@app.post("/users")
async def sign_up(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
                  user_type: Annotated[str, Body()]) -> UserData | Error:
    """
    Adds a new user to the system
    """
    try:
       data= UserToken(id_token=credentials.credentials)
       endpoint = f"http://users/users/signup/{user_type}"
       users_response = await post(endpoint, body=data.model_dump())
       return await recover_json_data(users_response) 
    except Exception as e:
        return Error.from_exception(e, endpoint="/users")

