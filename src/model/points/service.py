from fastapi import HTTPException, status
from src.model.points.point import Point, PointResponse
from src.model.points.provider import PointsProvider


class PointService():
    
    def __init__(self, provider: PointsProvider):
        self.provider = provider

    async def store_points(self, points: Point) -> None:
        try:
            return await self.provider.update_points(points)
        except Exception as e:
            raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=e.__str__()
                    )
    
    async def get_points(self, user: str) -> PointResponse:
        try:
            return await self.provider.get_points(user)
        except Exception as e:
            raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=e.__str__()
                   )
