from typing import Callable, List, Optional, Tuple

from fastapi import Query
from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session
from src.model.venues.data.base import MockBase, RelBase, VenuesBase
from src.model.venues.data.schema import VenueSchema
import datetime


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



    def _get_by_id(self, id: str) -> List[VenueSchema]:
        value = self.db.get_venue_by_id(id)
        return [value] if value else []


    def get(self,
            id: Optional[str],
            name: Optional[str],
            location: Optional[str],
            capacity: Optional[int],
            logo: Optional[str],
            pictures: Optional[List[str]],
            slots: Optional[List[datetime.datetime]],
            characteristics: Optional[List[str]],
            features: Optional[List[str]],
            vacations: Optional[List[datetime.datetime]],
            reservationLeadTime: Optional[int],
            menu: Optional[str],
            limit: int,
            start: int) -> Tuple[List[VenueSchema], int]:

        raise Exception("Interface method should not be called")

class RelBuilder(QueryBuilder):

    def __get_total(self) -> Select:
        return select(func.count()).select_from(VenueSchema)

    def __get_query(self, limit: int, start: int) -> Select:
        return select(VenueSchema).order_by(VenueSchema.id).limit(limit).offset(start)

    def __add_name_filter(self, name: Optional[str], query: Select, count: Select) -> Tuple[Select, Select]:
        if name: 
            query = query.where(VenueSchema.name.__eq__(name))
            count = count.where(VenueSchema.name.__eq__(name))
        return query, count
    
    def __add_characteristic_filter(self, characteristic: Optional[List[str]], query: Select, count: Select) -> Tuple[Select, Select]:
        if characteristic: 
            query = query.where(VenueSchema.characteristics.contains(characteristic))
            count = count.where(VenueSchema.characteristics.contains(characteristic))
        return query, count
    
    def __add_feature_filter(self, feature: Optional[List[str]], query: Select, count: Select) -> Tuple[Select, Select]:
        if feature: 
            query = query.where(VenueSchema.features.contains(feature))
            count = count.where(VenueSchema.features.contains(feature))
        return query, count

    def get(self, id: Optional[str], name: Optional[str], location: Optional[str], capacity: Optional[int], logo: Optional[str], pictures: Optional[List[str]], slots: Optional[List[datetime.datetime]], characteristic: Optional[List[str]], feature: Optional[List[str]], vacations: Optional[List[datetime.datetime]], reservationLeadTime: Optional[int], menu: Optional[str],limit: int, start: int) -> Tuple[List[VenueSchema],int]:
        if capacity != None or location != None or logo != None or pictures != None or slots != None  or vacations != None or reservationLeadTime != None or menu != None:
            raise Exception("Capacity, location, logo, pictures, menu and slots query not implemented")
        if id:
            result = self._get_by_id(id)
            return result, 1 if result else 0

        query = self.__get_query(limit, start)
        count = self.__get_total()

        query, count = self.__add_name_filter(name, query, count)
        query, count = self.__add_characteristic_filter(characteristic, query, count)  
        query, count = self.__add_feature_filter(feature, query, count) 

        return self.db.get_by_eq(query, count)     

class MockedBuilder(QueryBuilder):

    def __init__(self, db: MockBase) -> None:
        self.db = db

    def __filter(self, values: List[VenueSchema], by: Callable[[VenueSchema], bool], limit: int, start: int) -> List[VenueSchema]:
        result = []
        for value in values:
            if by(value):
                result.append(value)
        return result[start:start+limit]

    def __filter_by_name(self, name: str) -> Callable[[VenueSchema], bool]:
        def filter(value: VenueSchema) -> bool:
            return value.name == name
        return filter

    
    def __filter_by_characteristic(self, characteristic: List[str]) -> Callable[[VenueSchema], bool]:
        def filter(value: VenueSchema) -> bool:
            return any([c in value.characteristics for c in characteristic])
        return filter
    
    def __filter_by_feature(self, feature: List[str]) -> Callable[[VenueSchema], bool]:
        def filter(value: VenueSchema) -> bool:
            return any([c in value.features for c in feature])
        return filter

    def get(self, id: Optional[str], name: Optional[str], location: Optional[str], capacity: Optional[int] , logo: Optional[str], pictures: Optional[List[str]], slots: Optional[List[datetime.datetime]], characteristic: Optional[List[str]], feature: Optional[List[str]], vacations: Optional[List[datetime.datetime]], reservationLeadTime: Optional[int], menu: Optional[str], limit: int, start: int) -> Tuple[List[VenueSchema], int]:
        if capacity != None or location != None or logo != None or pictures != None or slots != None or  vacations != None or reservationLeadTime != None or menu != None:
            raise Exception("Capacity, location, logo, pictures, menu and slots query not implemented")

        if id:
            result = self._get_by_id(id)
            return result, 1 if result else 0

        result = self.__filter_by_eq(name, characteristic, feature, limit, start)

        return result, len(result) 



    def __filter_by_eq(self, name: Optional[str], characteristic: Optional[List[str]], feature: Optional[List[str]], limit: int, start: int) -> List[VenueSchema]:
        result = self.db.base

        if name:
            result = self.__filter(result, self.__filter_by_name(name), limit, start)

        if characteristic:
            result = self.__filter(result, self.__filter_by_characteristic(characteristic), limit, start)

        if feature:
            result = self.__filter(result, self.__filter_by_feature(feature), limit, start)

        return result