from datetime import datetime
from typing import Callable, List, Optional, Tuple

from fastapi import Query
from sqlalchemy import Select, select
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


class QueryBuilder: 
 
    def __init__(self, db: ReservationsBase) -> None:
        self.db = db

    def _get_by_id(self, id: str) -> List[ReservationSchema]:
        value = self.db.get_reservation_by_id(id)
        return [value] if value else []
    
    def __filter_by_eq(self, user: Optional[str], venue: Optional[str]) -> List[ReservationSchema]:
        raise Exception("Interface method should not be called")


    def get(self,
            id: Optional[str],
            user: Optional[str],
            status: Optional[str],
            venue: Optional[str],
            time: Optional[Tuple[datetime, datetime]],
            people: Optional[Tuple[int, int]],
            limit: int,
            start: int) -> List[ReservationSchema]:
        
        raise Exception("Interface method should not be called")

class RelBuilder(QueryBuilder):
    def __add_user_filter(self, query: Select, user: Optional[str]) -> Select:
        if user:
            query = query.where(ReservationSchema.user.__eq__(user))
        return query
    
    def __add_venue_filter(self, query: Select, venue: Optional[str]) -> Select:
        if venue:
            query = query.where(ReservationSchema.venue.__eq__(venue))
        return query
    
    def __add_status_filter(self, query: Select, status: Optional[str]) -> Select:
        if status:
            query = query.where(ReservationSchema.status.__eq__(status))

        return query

    def __add_time_filter(self, query: Select, limits: Optional[Tuple[datetime, datetime]]) -> Select:
        if limits:
            query = query.where(ReservationSchema.time.__ge__(limits[0]) & ReservationSchema.time.__le__(limits[1]))

        return query
    
    def __add_people_filter(self, query: Select, limits: Optional[Tuple[int, int]]) -> Select:
        if limits:
            query = query.where(ReservationSchema.people.__ge__(limits[0]) & ReservationSchema.people.__le__(limits[1]))

        return query
    
    def __get_initial(self, limit: int, start: int) -> Select:
        return select(ReservationSchema).limit(limit).offset(start)

    def get(self, id: Optional[str], user: Optional[str], status: Optional[str], venue: Optional[str], time: Optional[Tuple[datetime, datetime]], people: Optional[Tuple[int, int]], limit: int, start: int) -> List[ReservationSchema]:

        if id:
            return self._get_by_id(id)
    
        query = self.__get_initial(limit, start)
        query = self.__add_user_filter(query, user)
        query = self.__add_status_filter(query, status)
        query = self.__add_venue_filter(query, venue)
        query = self.__add_time_filter(query, time)
        query = self.__add_people_filter(query, people)
        query = query.order_by(ReservationSchema.time.desc())
        return self.db.get_by_eq(query)


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
    
    def get(self, id: Optional[str], user: Optional[str], status: Optional[str], venue: Optional[str], time: Optional[Tuple[datetime, datetime]], people: Optional[Tuple[int, int]], limit: int, start: int) -> List[ReservationSchema]:
        if time != None or people != None:
            raise Exception("Timed and people query not implemented")

        if id:
            return self._get_by_id(id)
        
        return self.__filter_by_eq(user, venue, limit, start)        



    def __filter_by_eq(self, user: Optional[str], venue: Optional[str], limit: int, start: int) -> List[ReservationSchema]:
        result = self.db.base
        
        if user:
            result = self.__filter(result, self.__filter_by_user(user), limit, start)
        if venue:
            result = self.__filter(result, self.__filter_by_venue(venue), limit, start)

        return result







