from typing import Annotated
from fastapi import Body, FastAPI, Response, Request
from src.model.gateway import HelloResponse
from fastapi.responses import JSONResponse
import requests as r

from src.model.users.auth_request import AuthRequest
from src.model.users.user_data import UserData


app = FastAPI()


@app.get("/{name}")
async def hello(name: str) -> HelloResponse:
   return HelloResponse(name=f"Hello, {name}") 

@app.get("/users/health")
async def users_health(response: Response):
    users_response = r.get("http://users/health")
    response.status_code = users_response.status_code

@app.post("/users")
async def get_data(request: Annotated[AuthRequest, Body()]) -> UserData:
    users_response = r.post("http://users/users", data=request.model_dump_json())
    
    return users_response.json()
    
