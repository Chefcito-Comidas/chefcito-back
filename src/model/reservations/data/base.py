from typing import List
from sqlalchemy.orm import Session
from src.model.reservations.data.schema import ReservationSchema
from sqlalchemy import create_engine, select, update

# TODO: try to add this to configuration options
DEFAULT_POOL_SIZE = 10

class ReservationsBase:
    
    def store_reservation(self, reservation: ReservationSchema) -> None:
        """
            Stores a reservation on the base, 
            if the reservation is already stored then 
            fails
        """
        raise Exception("Interface method should not be called")
    
    def update_reservation(self, reservation: ReservationSchema) -> None:
        """
            Updates information about a reservation
        """
        raise Exception("Interface method should not be called")
        
    def get_reservation_by_id(self, id: str) -> ReservationSchema | None:
        """
            Searches for a reservation based on the id 
            given
        """
        raise Exception("Interface method should not be called")


class RelBase(ReservationsBase):

    def __init__(self, conn_string: str, **kwargs):
        kwargs["pool_size"] = kwargs.get("pool_size", DEFAULT_POOL_SIZE)
        self.__engine = create_engine(conn_string, **kwargs)
    
    def store_reservation(self, reservation: ReservationSchema) -> None:
       session = Session(self.__engine)
       session.add(reservation)
       session.commit()
       session.close()

    def update_reservation(self, reservation: ReservationSchema) -> None:
        session = Session(self.__engine)
        value = session.get(ReservationSchema, reservation.id)
        if not value:
            return
        value.status = reservation.status
        value.time = reservation.time
        value.people = reservation.people
        session.commit()
        session.close()

    def get_reservation_by_id(self, id: str) -> ReservationSchema | None:
       session = Session(self.__engine)
       query = select(ReservationSchema).where(ReservationSchema.id.__eq__(id))
       result = session.scalar(query)
       session.close()
       return result

class MockBase(ReservationsBase):

    def __init__(self):
        self.base: List[ReservationSchema] = []

    def store_reservation(self, reservation: ReservationSchema) -> None:
        for stored in self.base:
            if stored.id == reservation.id:
                raise Exception("Reservation already exists")
        self.base.append(reservation)
    
    
    def update_reservation(self, reservation: ReservationSchema) -> None:
        for index, stored in enumerate(self.base):
            if stored.id == reservation.id:
                self.base[index] = reservation
                return

    def get_reservation_by_id(self, id: str) -> ReservationSchema | None:
        for stored in self.base:
            if stored.id == id:
                return stored
