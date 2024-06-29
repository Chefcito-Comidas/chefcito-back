from typing import Callable, List, Optional, Tuple

from fastapi import Query
from sqlalchemy import select
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
            venue: Optional[str],
            time: Optional[Tuple[str, str]],
            people: Optional[Tuple[int, int]],
            limit: int,
            start: int) -> List[ReservationSchema]:
        
        raise Exception("Interface method should not be called")

class RelBuilder(QueryBuilder):
    def __filter_by_eq(self, user: Optional[str], venue: Optional[str], limit: int, start: int) -> List[ReservationSchema]:
        query = select(ReservationSchema).order_by(ReservationSchema.id).limit(limit).offset(start)
        if user:
            query = query.where(ReservationSchema.user.__eq__(user))
        if venue:
            query = query.where(ReservationSchema.venue.__eq__(venue))
        
        return self.db.get_by_eq(query)
    
    def get(self, id: Optional[str], user: Optional[str], venue: Optional[str], time: Optional[Tuple[str, str]], people: Optional[Tuple[int, int]], limit: int, start: int) -> List[ReservationSchema]:
        if time != None or people != None:
            raise Exception("Timed and people query not implemented")

        if id:
            return self._get_by_id(id)
        
        return self.__filter_by_eq(user, venue, limit, start)        



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
    
    def get(self, id: Optional[str], user: Optional[str], venue: Optional[str], time: Optional[Tuple[str, str]], people: Optional[Tuple[int, int]], limit: int, start: int) -> List[ReservationSchema]:
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







