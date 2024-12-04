from typing import Any, Callable, List, Tuple
from src.model.commons.session import with_no_commit
from src.model.venues.data.schema import VenueSchema
from sqlalchemy import Engine, Result, Select, create_engine, select, update, delete
from sqlalchemy.orm import Session
from uuid import UUID

# TODO: try to add this to configuration options
DEFAULT_POOL_SIZE = 1

class VenuesBase:

    def get_by_eq(self, query: Select, count: Select) -> Tuple[List[VenueSchema], int]:
        raise Exception("Interface method should not be used")

    def store_venue(self, venue: VenueSchema) -> None:
        """
            Stores a venue on the base, 
            if the venue is already stored then 
            fails
        """
        raise Exception("Interface method should not be called")

   
    
    def update_venue(self, venue: VenueSchema) -> None:
        """
            Updates information about a venue
        """
        raise Exception("Interface method should not be called")
    
    def delete_venue(self, id: str) -> None:
        """
            Deletes a venue
        """
        raise Exception("Interface method should not be called")
    
    def get_venue_by_id(self, id: str) -> VenueSchema | None:

        """
            Searches for a venue based on the id 
            given
        """
        raise Exception("Interface method should not be called")
from sqlalchemy.orm import sessionmaker, scoped_session

class RelBase(VenuesBase):
    def __init__(self, conn_string: str, **kwargs):
        kwargs["pool_size"] = kwargs.get("pool_size", DEFAULT_POOL_SIZE)
        self.__engine = create_engine(conn_string, pool_pre_ping=True,**kwargs)

    def __get_runnable_select(self, query: Select) -> Callable[[Engine], Result]:
        def call(session: Session) -> List[Any]:
            return list(session.execute(query).scalars())

        return with_no_commit(call)

    def get_by_eq(self, query: Select, count: Select) -> Tuple[List[VenueSchema], int]:
        venues: List[VenueSchema] = self.__get_runnable_select(query)(self.__engine) # type: ignore
        total: int = self.__get_runnable_select(count)(self.__engine).pop() # type: ignore
        return venues, total 

    def store_venue(self, venue: VenueSchema) -> None:
        session = Session(self.__engine)
        session.add(venue)
        session.commit()
        session.close()

    def update_venue(self, venue: VenueSchema) -> None:
        session = Session(self.__engine)
        value = session.get(VenueSchema, venue.id)
        if not value:
            return
        value.name = venue.name
        value.location = venue.location
        value.capacity = venue.capacity
        value.logo = venue.logo
        value.pictures = venue.pictures
        value.slots = venue.slots
        value.characteristics = venue.characteristics
        value.features = venue.features
        value.vacations = venue.vacations
        value.reservationLeadTime = venue.reservationLeadTime
        value.menu = venue.menu
        value.status = venue.status
        session.commit()
        session.close()

    def get_venue_by_id(self, id: str) -> VenueSchema | None:
        session = Session(self.__engine)
        query = select(VenueSchema).where(VenueSchema.id.__eq__(id))
        result = session.scalar(query)
        session.close()
        return result
    
    def delete_venue(self, id: str) -> None:
        session = Session(self.__engine)
        query = delete(VenueSchema).where(VenueSchema.id.__eq__(id))
        session.execute(query)
        session.commit()
        session.close()
        return
    
    



class MockBase(VenuesBase):

    def __init__(self):
        self.base: List[VenueSchema] = []

    def store_venue(self, venue: VenueSchema) -> None:
        for stored in self.base:
            if stored.id == venue.id:
                raise Exception("Venue already exists")
        self.base.append(venue)


    def update_venue(self, venue: VenueSchema) -> None:
        for index, stored in enumerate(self.base):
            if stored.id == venue.id:
                self.base[index] = venue
                return
       

    def get_venue_by_id(self, id: str) -> VenueSchema | None:
        for stored in self.base:
            if stored.id == id:
                return stored
    
    def delete_venue(self, id: str) -> None:
        for index, stored in enumerate(self.base):
            if stored.id == id:
                self.base.pop(index)
                return
        return
