from fastapi import FastAPI, Response, status, Query, Body
from pydantic_settings import BaseSettings
from src.model.commons.error import Error
from src.model.users.auth_request import AuthRequest
from src.model.users.firebase.api_instance import FirebaseClient
from src.model.users.permissions.base import DBEngine
from src.model.users.user_data import UserData, UserToken

from typing import Annotated, Any, Dict

class Settings(BaseSettings):
    api_key: str = "ultraSecret"
    db_string: str = "database_conn_string"

settings = Settings()
app = FastAPI()

authenticator = FirebaseClient(key=settings.api_key)
database = DBEngine(conn_string=settings.db_string)

@app.get("/health")
async def health(response: Response):
    response.status_code = status.HTTP_200_OK

@app.post("/users/signup/{user_type}")
async def sign_up(user_type: str, token: Annotated[UserToken, Body()], response: Response) -> UserData | Error:
    """
    Recieve the token, get the user data for the token and add it
    to the database
    """
    try:
        user = await token.get_data(authenticator)
        user.insert_into(user_type, database)
        return user
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return Error.from_exception(e, endpoint="/signup") 
        

@app.post("/users/signin")
async def sign_in(email: Annotated[str, Query()], password: Annotated[str, Query()]) -> Dict[str, Any]:
    """
    Use this to get the when someone is signing in
    Ask for the token only
    """  
    return await authenticator.sign_in(email, password) 

@app.post("/users")
async def get_data(auth: Annotated[UserToken, Body()], response: Response) -> UserData | Error:
    """
    Returns all data from the user, including its type
    """
    try:
        return await auth.get_data(authenticator) 
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return Error.from_exception(e, endpoint="/users") 

@app.post("/users/permissions")
async def is_allowed(auth: Annotated[AuthRequest, Body()], response: Response) -> None | Error:
    """
    Checks if the user is allowed or not to access a certain endpoint
    """
    try:
        response.status_code = status.HTTP_200_OK if await auth.is_allowed(authenticator, database) \
                else status.HTTP_403_FORBIDDEN
    except Exception as e:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return Error.from_exception(e, endpoint="/permissions")
