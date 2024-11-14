import asyncio
from datetime import datetime
from typing import Callable, List, Optional, Tuple

from fastapi import Query
from pydantic import BaseModel
from sqlalchemy import Select, desc, func, select
from sqlalchemy.orm import Session
from src.model.reservations.data.base import MockBase, RelBase, ReservationsBase
from src.model.reservations.data.schema import ReservationSchema

def get_builder(db: ReservationsBase) -> 'QueryBuilder':
    """
        Returns the builder type based on the parameter passed
        to it.
    """
    if isinstance(db, MockBase):
        return MockedBuilder(db)

    return RelBuilder(db)


class QueryResult():

    def __init__(self, result: List[ReservationSchema], total: int):
        self.result = result
        self.total = total

class QueryBuilder:

    def __init__(self, db: ReservationsBase) -> None:
        self.db = db

    def _get_by_id(self, id: str) -> List[ReservationSchema]:
        value = self.db.get_reservation_by_id(id)
        return [value] if value else []

    def __filter_by_eq(self, user: Optional[str], venue: Optional[str]) -> List[ReservationSchema]:
        raise Exception("Interface method should not be called")


    async def get(self,
            id: Optional[str],
            user: Optional[str],
            status: Optional[List[str]],
            venue: Optional[str],
            time: Optional[Tuple[datetime, datetime]],
            people: Optional[Tuple[int, int]],
            limit: int,
            start: int) -> QueryResult:

        raise Exception("Interface method should not be called")

class RelBuilder(QueryBuilder):
    def __add_user_filter(self, query: Select, count: Select, user: Optional[str]) -> Tuple[Select, Select]:
        if user:
            query = query.where(ReservationSchema.user.__eq__(user))
            count = count.where(ReservationSchema.user.__eq__(user))
        return query,count

    def __add_venue_filter(self, query: Select, count: Select, venue: Optional[str]) -> Tuple[Select,Select]:
        if venue:
            query = query.where(ReservationSchema.venue.__eq__(venue))
            count = count.where(ReservationSchema.venue.__eq__(venue))
        return query,count

    def __add_status_filter(self, query: Select, count:Select, status: Optional[List[str]]) -> Tuple[Select,Select]:
        if status:
            query = query.where(ReservationSchema.status.in_(status))
            count = count.where(ReservationSchema.status.in_(status))
        return query,count

    def __add_time_filter(self, query: Select, count: Select, limits: Optional[Tuple[datetime, datetime]]) -> Tuple[Select,Select]:
        if limits:
            query = query.where(ReservationSchema.time.__ge__(limits[0]) & ReservationSchema.time.__le__(limits[1]))
            count = count.where(ReservationSchema.time.__ge__(limits[0]) & ReservationSchema.time.__le__(limits[1]))
        return query,count

    def __add_people_filter(self, query: Select, count: Select, limits: Optional[Tuple[int, int]]) -> Tuple[Select,Select]:
        if limits:
            query = query.where(ReservationSchema.people.__ge__(limits[0]) & ReservationSchema.people.__le__(limits[1]))
            count = count.where(ReservationSchema.people.__ge__(limits[0]) & ReservationSchema.people.__le__(limits[1]))
        return query,count

    def __get_initial(self, limit: int, start: int) -> Select:
        return select(ReservationSchema).limit(limit).offset(start)

    def __get_count(self) -> Select:
        return select(func.count()).select_from(ReservationSchema)

    async def get(self, id: Optional[str], user: Optional[str], status: Optional[List[str]], venue: Optional[str], time: Optional[Tuple[datetime, datetime]], people: Optional[Tuple[int, int]], limit: int, start: int) -> QueryResult:
        loop = asyncio.get_event_loop()
        if id:
            return QueryResult(result=self._get_by_id(id), total=1)

        query = self.__get_initial(limit, start)
        count_query = self.__get_count()
        query, count_query = self.__add_user_filter(query, count_query, user)
        query, count_query = self.__add_status_filter(query, count_query, status)
        query, count_query = self.__add_venue_filter(query,count_query, venue)
        query, count_query = self.__add_time_filter(query,count_query, time)
        query, count_query = self.__add_people_filter(query,count_query, people)
        result = loop.run_in_executor(None,self.db.get_by_eq, query.order_by(desc(ReservationSchema.time))
        count = loop.run_in_executor(None, self.db.run_count,count_query)
        return QueryResult(result=await result, total=await count)

class MockedBuilder(QueryBuilder):

    def __init__(self, db: MockBase):
        self.db = db

    def __filter(self, values: List[ReservationSchema], by: Callable[[ReservationSchema], bool], limit: int, start: int) -> List[ReservationSchema]:
        result = []
        for value in values:
            if by(value):
                result.append(value)
        return result[start:start+limit]

    def __filter_by_user(self, user: str) -> Callable[[ReservationSchema], bool]:
        def filter(value: ReservationSchema) -> bool:
            return value.user == user
        return filter

    def __filter_by_venue(self, venue: str) -> Callable[[ReservationSchema], bool]:
        def filter(value: ReservationSchema) -> bool:
            return value.venue == venue
        return filter

    async def get(self, id: Optional[str], user: Optional[str], status: Optional[List[str]], venue: Optional[str], time: Optional[Tuple[datetime, datetime]], people: Optional[Tuple[int, int]], limit: int, start: int) -> QueryResult:
        if time != None or people != None:
            raise Exception("Timed and people query not implemented")

        if id:
            return QueryResult(result=self._get_by_id(id),total=1)

        result = self.__filter_by_eq(user, venue, limit, start)
        return QueryResult(result=result, total=len(result))


    def __filter_by_eq(self, user: Optional[str], venue: Optional[str], limit: int, start: int) -> List[ReservationSchema]:
        result = self.db.base

        if user:
            result = self.__filter(result, self.__filter_by_user(user), limit, start)
        if venue:
            result = self.__filter(result, self.__filter_by_venue(venue), limit, start)

        return result
