from typing import Annotated
from fastapi import Body, FastAPI, Path
from pydantic_settings import BaseSettings

from src.model.points.data.base import RelPointBase
from src.model.points.point import Point, PointResponse
from src.model.points.provider import LocalPointsProvider
from src.model.points.service import PointService 

class Settings(BaseSettings):
    conn_string: str = "" 

settings = Settings()

base = RelPointBase(settings.conn_string)
provider = LocalPointsProvider(base)
service = PointService(provider)

app = FastAPI()


@app.get("/points/{user}")
async def retrieve_points(user: Annotated[str, Path()]) -> PointResponse:
    return await service.get_points(user)

@app.post("/points")
async def store_points(points: Annotated[Point, Body()]) -> None:
    return await service.store_points(points)
