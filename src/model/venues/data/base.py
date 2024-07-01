from typing import List
from src.model.venues.data.schema import VenueSchema
from sqlalchemy import Select, create_engine, select, update
from sqlalchemy.orm import Session

# TODO: try to add this to configuration options
DEFAULT_POOL_SIZE = 10

class VenuesBase:

    def get_by_eq(self, query: Select) -> List[VenueSchema]:
        raise Exception("Interface method should not be used")

    def store_venue(self, venue: VenueSchema) -> None:
        """
            Stores a venue on the base, 
            if the venue is already stored then 
            fails
        """
        raise Exception("Interface method should not be called")

    def get_by_eq(self, query: Select) -> List[VenueSchema]:
        session = Session(self.__engine)
        return list(session.scalars(query).fetchmany(100))
    
    def update_venue(self, reservation: VenueSchema) -> None:
        """
            Updates information about a reservation
        """
        raise Exception("Interface method should not be called")
    
    def get_venue_by_id(self, id: str) -> VenueSchema | None:

        """
            Searches for a reservation based on the id 
            given
        """
        raise Exception("Interface method should not be called")
from sqlalchemy.orm import sessionmaker, scoped_session

class RelBase(VenuesBase):
    def __init__(self, conn_string: str, **kwargs):
        kwargs["pool_size"] = kwargs.get("pool_size", DEFAULT_POOL_SIZE)
        self.__engine = create_engine(conn_string, **kwargs)

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
        value.status = venue.status
        session.commit()
        session.close()

    def get_venue_by_id(self, id: str) -> VenueSchema | None:
        session = Session(self.__engine)
        query = select(VenueSchema).where(VenueSchema.id.__eq__(id))
        result = session.scalar(query)
        session.close()
        return result



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
