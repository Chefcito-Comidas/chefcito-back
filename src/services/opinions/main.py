from typing import Annotated
from fastapi import Body, FastAPI, Path
from pydantic_settings import BaseSettings

from src.model.opinions.service import LocalOpinionsProvider, OpinionsService


class Settings(BaseSettings):
    pass

settings = Settings()

app = FastAPI()
opinions = OpinionsService(LocalOpinionsProvider())


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
async def create_opinion(opinion: Annotated[str, Body()]):
    return await opinions.create_opinion(opinion)

@app.get("/opinions")
async def query_opinions(query: Annotated[str, Body()]):
    return await opinions.query_opinions(query)

@app.get("/summaries/{restaurant}")
async def get_summary(restaurant: Annotated[str, Path()]):
    return await opinions.get_summary(restaurant)

@app.post("/summaries/{restaurant}")
async def create_summary(restaurant: Annotated[str, Path()]):
    return await opinions.create_new_summary(restaurant)
