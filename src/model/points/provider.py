from datetime import datetime
from typing import List
from src.model.commons.caller import post, get, recover_json_data
from src.model.commons.logger import Logger
from src.model.points.data.base import PointBase
from src.model.points.point import Point, PointResponse

DEFAULT_LEVELS = ["Novato",
                  "Aficionado Gourmet",
                  "Comensal Amateur",
                  "Comensal Experto",
                  "Estrella Culinaria"]

class PointsProvider():

    async def update_points(self, points: Point, time: datetime = datetime.now()) -> None:
        raise Exception("Interface method should not be called")

    async def get_points(self, user: str) -> PointResponse:
        raise Exception("Interface method should not be called")

class HttpPointsProvider(PointsProvider):

    def __init__(self, url: str):
        self.url = url

    async def update_points(self, points: Point, time: datetime = datetime.now()) -> None:
        endpoint = "/points"
        Logger.info(f"Posting opinions: {points.model_dump()}")
        await post(f"{self.url}{endpoint}", body=points.model_dump())

    async def get_points(self, user: str) -> PointResponse:
        endpoint = f"/points/{user}"
        print(f"{self.url}{endpoint}")
        response = await get(f"{self.url}{endpoint}")
        return await recover_json_data(response)

class LocalPointsProvider(PointsProvider):

    def __init__(self, base: PointBase, levels: List[str] = DEFAULT_LEVELS):
        self.base = base
        self.levels = levels

    async def update_points(self, points: Point, time: datetime = datetime.now()) -> None:
        return await self.base.update_points(points, time=time)

    async def get_points(self, user: str) -> PointResponse:
        result = await self.base.recover_points(user)
        if not result:
            result = Point(total=0, user=user)
        return result.into_response(levels=self.levels)
