from contextlib import asynccontextmanager
from typing import Annotated
from fastapi import FastAPI, Path
from pydantic_settings import BaseSettings

from src.model.reservations.reservation import Reservation
from src.model.stats.data.base import MongoStatsDB
from src.model.stats.provider import GET_USER_DATA_ENDPOINT, GET_VENUE_DATA_ENDPOINT, UPDATE_ENDPOINT, LocalStatsProvider
from src.model.stats.service import StatsService
from src.model.stats.stats_update import StatsUpdate
from src.model.stats.user_data import UserStatData
from src.model.stats.venue_data import VenueStatData


class Settings(BaseSettings):
    mongo_string: str = ""

settings = Settings()

database = MongoStatsDB(settings.mongo_string)

@asynccontextmanager
async def init_services(app: FastAPI):
    await database.init()
    yield

app = FastAPI(lifespan=init_services)
stats = StatsService(LocalStatsProvider(database))


@app.post(UPDATE_ENDPOINT)
async def update_call(reservation: Reservation) -> None:
    return await stats.update(reservation)

@app.get(GET_USER_DATA_ENDPOINT + "{user}")
async def get_user_data(user: Annotated[str, Path()])-> UserStatData:
    return await stats.get_user(user)

@app.get(GET_VENUE_DATA_ENDPOINT + "{venue}")
async def get_venue_data(venue: Annotated[str, Path()]) -> VenueStatData:
    return await stats.get_venue(venue)
