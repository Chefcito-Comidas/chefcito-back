import asyncio
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Annotated, Any, List, Optional
from fastapi import Body, FastAPI, Path, Query
from pydantic_settings import BaseSettings
from src.model.opinions.data.base import MongoOpinionsDB
from src.model.opinions.opinion import Opinion
from src.model.opinions.opinion_query import OpinionQuery, OpinionQueryResponse
from src.model.opinions.provider import LocalOpinionsProvider
from src.model.opinions.service import OpinionsService
from src.model.commons.error import Error
from src.model.summarizer.summary import Summary
from src.model.summarizer.provider import HttpSummarizerProvider, SummarizerService

class Settings(BaseSettings):
    conn_string: str
    summaries: str = "http://summaries"

settings = Settings()

database = MongoOpinionsDB(settings.conn_string)

@asynccontextmanager
async def init_database(app: FastAPI):
    await database.init()
    yield

app = FastAPI(lifespan=init_database)
summaries = SummarizerService(HttpSummarizerProvider(settings.summaries))
opinions = OpinionsService(LocalOpinionsProvider(database), summaries)


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
async def create_opinion(opinion: Annotated[Opinion, Body()]) -> Opinion | Error:
    return await opinions.create_opinion(opinion)

@app.get("/opinions")
async def query_opinions(venue: Optional[str] = Query(default=None),
                         from_date: Optional[datetime] = Query(default=None),
                         to_date: Optional[datetime] = Query(default=None),
                         limit: int = Query(default=10),
                         start: int = Query(default=0)) -> OpinionQueryResponse | Error:
    query = OpinionQuery(
        venue=venue,
        from_date=from_date,
        to_date=to_date,
        limit=limit,
        start=start
    )
    return await opinions.query_opinions(query)

@app.get("/summaries/{restaurant}")
async def get_summary(restaurant: Annotated[str, Path()],
                      limit: Annotated[int, Query()] = 3,
                      skip: Annotated[int, Query()] = 0) -> List[Summary] | Error:
    return await opinions.get_summary(restaurant, limit, skip)

@app.post("/summaries/{restaurant}")
async def create_summary(restaurant: Annotated[str, Path()]) -> Any | Error:
    return await opinions.create_new_summary(restaurant)
