from fastapi import FastAPI, Response, status, Query, Body
from pydantic_settings import BaseSettings
from src.model.users.auth_request import AuthRequest
from src.model.users.firebase.api_instance import FirebaseClient
from src.model.users.user_data import UserData

from typing import Annotated, Any, Dict

class Settings(BaseSettings):
    api_key: str = "ultraSecret"

settings = Settings()
app = FastAPI()

authenticator = FirebaseClient(key=settings.api_key)

@app.get("/health")
async def health(response: Response):
    response.status_code = status.HTTP_200_OK

@app.post("/users/signup")
async def sign_up():
    pass

@app.post("/users/signin")
async def sign_in(email: Annotated[str, Query()], password: Annotated[str, Query()]) -> Dict[str, Any]:
    return authenticator.sign_in(email, password) 

@app.post("/users")
async def get_data(auth: Annotated[AuthRequest, Body()]) -> UserData:
   return await auth.get_data(authenticator) 

