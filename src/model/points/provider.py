from src.model.commons.caller import post, get, recover_json_data
from src.model.points.data.base import PointBase
from src.model.points.point import Point


class PointsProvider():
    
    async def update_points(self, points: Point) -> None:
        raise Exception("Interface method should not be called")
    
    async def get_points(self, user: str) -> Point:
        raise Exception("Interface method should not be called")

class HttpPointsProvider(PointsProvider):
   
    def __init__(self, url: str):
        self.url = url

    async def update_points(self, points: Point) -> None:
        endpoint = "/points"
        await post(f"{self.url}{endpoint}", body=points.model_dump())
    
    async def get_points(self, user: str) -> Point:
        endpoint = f"/points/{user}"
        response = await get(f"{self.url}{endpoint}")
        return await recover_json_data(response)

class LocalPointsProvider(PointsProvider):
    
    def __init__(self, base: PointBase):
        self.base = base

    async def update_points(self, points: Point) -> None:
        return await self.base.update_points(points)

    async def get_points(self, user: str) -> Point:
        result = await self.base.recover_points(user)
        if not result:
            result = Point(total=0, user=user)
        return result
