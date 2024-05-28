from fastapi import FastAPI, Response, status, Query, Body
from pydantic_settings import BaseSettings
from src.model.commons.error import Error
from src.model.users.auth_request import AuthRequest
from src.model.users.firebase.api_instance import FirebaseClient
from src.model.users.permissions.base import DBEngine
from src.model.users.user_data import UserData, UserToken
from typing import Annotated, Any, Dict
from src.model.users.service import UsersService

class Settings(BaseSettings):
    api_key: str = "ultraSecret"
    db_string: str = "database_conn_string"

settings = Settings()
app = FastAPI()

authenticator = FirebaseClient(key=settings.api_key)
database = DBEngine(conn_string=settings.db_string)
service = UsersService(authenticator, database)

@app.get("/health")
async def health(response: Response):
    response.status_code = status.HTTP_200_OK

@app.post("/users/signup/{user_type}")
async def sign_up(user_type: str, token: Annotated[UserToken, Body()], response: Response) -> UserData | Error:
    return await service.sign_up(user_type, token, response)       

@app.post("/users/signin")
async def sign_in(email: Annotated[str, Query()], password: Annotated[str, Query()]) -> Dict[str, Any]:
    return await service.sign_in(email, password)    

@app.post("/users")
async def get_data(auth: Annotated[UserToken, Body()], response: Response) -> UserData | Error:
    return await service.get_data(auth, response)

@app.post("/users/permissions")
async def is_allowed(auth: Annotated[AuthRequest, Body()], response: Response) -> None | Error:
    return await service.is_allowed(auth, response)
