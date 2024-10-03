from datetime import datetime

from logging import log
import logging
from typing import Annotated, List
from fastapi import FastAPI, Path, Query
from contextlib import asynccontextmanager
from pydantic_settings import BaseSettings
from src.model.commons.error import Error
from src.model.opinions.data.base import MongoOpinionsDB
from src.model.summarizer.process.algorithm import SummaryAlgorithm, VertexSummarizer
import src.model.summarizer.process.prompt as prompt
from src.model.summarizer.service import LocalSummarizerProvider
from src.model.summarizer.provider import SummarizerService
from src.model.summarizer.summary import Summary
from src.model.summarizer.summary_query import SummaryQuery

class Settings(BaseSettings):
    conn_string: str = ""
    key_id: str = ""
    key: str = ""
    dev: bool = True


settings = Settings()

database = MongoOpinionsDB(settings.conn_string)
summarizer = SummaryAlgorithm(VertexSummarizer())

@asynccontextmanager
async def init_services(app: FastAPI):
    global summarizer
    await database.init()
    if settings.dev:
        summarizer = SummaryAlgorithm()
    else:
       try:
        prompt.init(settings.key, settings.key_id)
       except Exception as e:
          log(level=logging.CRITICAL, msg=e)
          summarizer = SummaryAlgorithm()
    yield

app = FastAPI(lifespan=init_services)
summaries = SummarizerService(LocalSummarizerProvider(database, summarizer))

@app.get("/summaries")
async def get_summary(venue: Annotated[str, Query()],
                      limit: Annotated[int, Query()] = 3,
                      skip: Annotated[int, Query()] = 0) -> List[Summary] | Error:
    query = SummaryQuery(
        venue=venue,
        limit=limit,
        skip=skip
    )
    return await summaries.get_summary(query)

@app.post("/summaries/{restaurant}")
async def create_summary(restaurant: Annotated[str, Path()],
                         since: Annotated[datetime, Query()]) -> Summary | Error:
    return await summaries.create_summary(restaurant, since)


