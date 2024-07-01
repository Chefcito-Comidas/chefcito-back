from typing import Callable, List, Optional, Tuple

from fastapi import Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from src.model.venues.data.base import MockBase, RelBase, VenuesBase
from src.model.venues.data.schema import VenueSchema


def get_builder(db: VenuesBase) -> 'QueryBuilder':
    """
        Returns the builder type based on the parameter passed
        to it.
    """
    if isinstance(db, MockBase):
        return MockedBuilder(db)

    return RelBuilder(db)

class QueryBuilder:

    def __init__(self, db: VenuesBase) -> None:
        self.db = db



    def get_by_id(self, id: str) -> List[VenueSchema]:
        value = self.db.get_venue_by_id(id)
        return [value] if value else []

    def __filter_by_eq(self, user: Optional[str], venue: Optional[str]) -> List[VenueSchema]:
        raise Exception("Interface method should not be called")

    def get(self,
            id: Optional[str],
            name: Optional[str],
            location: Optional[str],
            capacity: Optional[int]) -> List[VenueSchema]:

        raise Exception("Interface method should not be called")

class RelBuilder(QueryBuilder):

    def __filter_by_eq(self, name: Optional[str]) -> List[VenueSchema]:
        query = select(VenueSchema)
        if name:
            query = query.where(VenueSchema.name.__eq__(name))

        return self.db.get_by_eq(query)

    def get(self, id: Optional[str], name: Optional[str], location: Optional[str], capacity: Optional[int]) -> List[VenueSchema]:
        if capacity != None or location != None:
            raise Exception("Capacity and location query not implemented")
        if id:
            return self.__get_by_id(id)

        return self.__filter_by_eq(name)        

class MockedBuilder(QueryBuilder):

    def __init__(self, db: MockBase) -> None:
        self.db = db

    def __filter(self, values: List[VenueSchema], by: Callable[[VenueSchema], bool]) -> List[VenueSchema]:
        result = []
        for value in values:
            if by(value):
                result.append(value)
        return result

    def __filter_by_name(self, name: str) -> Callable[[VenueSchema], bool]:
        def filter(value: VenueSchema) -> bool:
            return value.name == name
        return filter


    def get(self, id: Optional[str], name: Optional[str], location: Optional[str], capacity: Optional[int]) -> List[VenueSchema]:
        if capacity != None or location != None:
            raise Exception("Capacity and location query not implemented")

        if id:
            return self.__get_by_id(id)

        return self.__filter_by_eq(name)        



    def __filter_by_eq(self, name: Optional[str]) -> List[VenueSchema]:
        result = self.db.base

        if name:
            result = self.__filter(result, self.__filter_by_name(name))

        return result