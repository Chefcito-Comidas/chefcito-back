import asyncio
from contextlib import asynccontextmanager
from typing import Annotated
from fastapi import Body, FastAPI, Path
from pydantic_settings import BaseSettings

from src.model.opinions.data.base import MongoOpinionsDB
from src.model.opinions.opinion import Opinion
from src.model.opinions.opinion_query import OpinionQuery
from src.model.opinions.service import LocalOpinionsProvider, OpinionsService


class Settings(BaseSettings):
    conn_string: str

settings = Settings()

database = MongoOpinionsDB(settings.conn_string)
@asynccontextmanager
async def init_database(app: FastAPI):
    await database.init()
    yield

app = FastAPI(lifespan=init_database)
opinions = OpinionsService(LocalOpinionsProvider(database))


"""
Endpoints: 

    1. /opinions
        - POST => create new opinion
        - GET => Get opinions from a restaurant
        - PUT => Modify opinion ? 
        - DELETE => Delete opinion ? 
    
    2. /summary
        - GET => Get latest summary of a 
        restaurant
        - POST => Ask to create a summary 
        of opinions of a restaurant
"""
    

@app.post("/opinions")
async def create_opinion(opinion: Annotated[Opinion, Body()]):
    return await opinions.create_opinion(opinion)

@app.get("/opinions")
async def query_opinions(query: Annotated[OpinionQuery, Body()]):
    return await opinions.query_opinions(query)

@app.get("/summaries/{restaurant}")
async def get_summary(restaurant: Annotated[str, Path()]):
    return await opinions.get_summary(restaurant)

@app.post("/summaries/{restaurant}")
async def create_summary(restaurant: Annotated[str, Path()]):
    return await opinions.create_new_summary(restaurant)
