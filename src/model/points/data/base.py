import asyncio
from typing import Any, Callable, Optional

from sqlalchemy import Select, create_engine, select
from src.model.commons.session import with_no_commit, with_session
from src.model.points.data.schema import PointSchema
from src.model.points.point import Point
from sqlalchemy.orm import Session

DEFAULT_POOL_BASE = 10

class PointBase():

    async def update_points(self, points: Point) -> None:
        raise Exception("Interface method should not be called")
    
    async def recover_points(self, user: str) -> Optional[Point]:
        raise Exception("Interface method should not be called")

class RelPointBase(PointBase):

    def __init__(self, url: str, **kwargs):
        kwargs["pool_size"] = kwargs.get("pool_size", DEFAULT_POOL_BASE)
        self.__engine = create_engine(url, pool_pre_ping=True, **kwargs)

    def __get_user_query(self, user: str) -> Callable[[Session], Optional[Point]]:
        def call(session: Session) -> Optional[Point]:
            query = select(PointSchema).where(PointSchema.user.__eq__(user))
            return session.scalar(query)
        return call

    def __get_update_query(self, points: Point) -> Callable[[Session], None]:
        def call(session: Session) -> None:
           value = session.get(PointSchema, points.user)
           value.total = points.total  

        return call

    def __get_insertion_query(self, points: Point) -> Callable[[Session], None]:
        def call(session: Session) -> None:
            session.add(PointSchema.from_points(points))
        return call

    async def update_points(self, points: Point) -> None:
        call = self.__get_user_query(points.user)
        loop = asyncio.get_event_loop()
        recovered_points = await loop.run_in_executor(None, with_no_commit(call), self.__engine)
        update = self.__get_insertion_query(points)
        if recovered_points:
           points.total += recovered_points.total
           update = self.__get_update_query(points)
        await loop.run_in_executor(None, with_session(update), self.__engine)
            
    async def recover_points(self, user: str) -> Point | None:
        call = self.__get_user_query(user)
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, with_no_commit(call), self.__engine) 

class MockedPointBase(PointBase):
    
    def __init__(self):
        self.point_base = {}

    async def update_points(self, points: Point) -> None:
        actual = self.point_base.get(points.user, Point(total=0, user=points.user))
        actual.total += points.total
        self.point_base[points.user] = actual

    async def recover_points(self, user: str) -> Optional[Point]:
        return self.point_base.get(user, None) 


