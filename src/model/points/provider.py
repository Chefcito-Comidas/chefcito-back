from src.model.points.point import Point


class PointsProvider():
    
    async def update_points(self, points: Point) -> None:
        raise Exception("Interface method should not be called")
    
    async def get_points(self, user: str) -> Point:
        raise Exception("Interface method should not be called")

class HttpPointsProvider(PointsProvider):
    pass

class LocalPointsProvider(PointsProvider):
    pass