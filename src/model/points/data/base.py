import asyncio
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Optional, Tuple

from sqlalchemy import Select, create_engine, select
from src.model.commons.session import with_no_commit, with_session
from src.model.points.data.schema import PointSchema
from src.model.points.point import Point
from sqlalchemy.orm import Session

DEFAULT_POOL_BASE = 5
DEFAULT_POINT_REBASE = timedelta(days=14)
DEFAULT_POINT_DISCOUNT = 200

class PointBase():

    async def update_points(self, points: Point, time: datetime = datetime.now()) -> None:
        raise Exception("Interface method should not be called")

    async def recover_points(self, user: str) -> Optional[Point]:
        raise Exception("Interface method should not be called")

class RelPointBase(PointBase):

    def __init__(self, url: str, **kwargs):
        kwargs["pool_size"] = kwargs.get("pool_size", DEFAULT_POOL_BASE)
        kwargs["pool_recyle"] = 30
        self.__engine = create_engine(url, pool_pre_ping=True, **kwargs)

    def __update_if_nedeed(self, value: PointSchema):
        if datetime.now() - value.last_updated >= DEFAULT_POINT_REBASE:
            value.total = value.total - 200 if value.total >= 200 else 0


    def __get_user_query(self, user: str) -> Callable[[Session], Optional[Point]]:
        def call(session: Session) -> Optional[Point]:
            query = select(PointSchema).where(PointSchema.user.__eq__(user))
            result = session.scalar(query)
            if result is not None:
                self.__update_if_nedeed(result)
            return result.into_points() if result else None
        return call

    def __get_update_query(self, points: Point, time: datetime) -> Callable[[Session], None]:
        def call(session: Session) -> None:
           value = session.get(PointSchema, points.user)
           if value is None:
               return
           value.total = points.total
           value.last_updated = time
        return call

    def __get_insertion_query(self, points: Point, time: datetime) -> Callable[[Session], None]:
        def call(session: Session) -> None:
            schema = PointSchema.from_points(points)
            schema.last_updated = time
            session.add(schema)
        return call

    async def update_points(self, points: Point, time: datetime = datetime.now()) -> None:
        call = self.__get_user_query(points.user)
        loop = asyncio.get_event_loop()
        recovered_points = await loop.run_in_executor(None, with_session(call), self.__engine)
        update = self.__get_insertion_query(points, time)
        if recovered_points:
           points.total += recovered_points.total
           update = self.__get_update_query(points, time)
        await loop.run_in_executor(None, with_session(update), self.__engine)

    async def recover_points(self, user: str) -> Point | None:
        call = self.__get_user_query(user)
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, with_session(call), self.__engine)


class MockedPointBase(PointBase):

    def __init__(self):
        self.point_base: Dict[str, Tuple[Point, datetime]] = {}

    def discount(self, points: Point, new_time: datetime):
        points.total -= DEFAULT_POINT_DISCOUNT
        self.point_base[points.user] = (points, new_time)

    async def update_points(self, points: Point, time: datetime = datetime.now()) -> None:
        actual,last_time = self.point_base.get(points.user, (Point(total=0, user=points.user),time))
        actual.total += points.total
        if time - last_time >= DEFAULT_POINT_REBASE:
            self.discount(actual, time)
        else:
            self.point_base[actual.user] = (actual,time)

    async def recover_points(self, user: str) -> Optional[Point]:
        actual, last_time = self.point_base.get(user, (None, datetime.now()))
        if actual is not None and datetime.now() - last_time >= DEFAULT_POINT_REBASE:
            self.discount(actual, datetime.now())

        return actual
