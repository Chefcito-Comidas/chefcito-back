from typing import List
from src.model.reservations.data.schema import ReservationSchema


class ReservationsBase:
    
    def store_reservation(self, reservation: ReservationSchema) -> None:
        """
            Stores a reservation on the base, 
            if the reservation is already stored then 
            updates the reservation value
        """
        raise Exception("Interface method should not be called")

    def get_reservation_by_id(self, id: str) -> ReservationSchema | None:
        raise Exception("Interface method should not be called")


class RelBase(ReservationsBase):
    pass


class MockBase(ReservationsBase):

    def __init__(self):
        self.base: List[ReservationSchema] = []

    def store_reservation(self, reservation: ReservationSchema) -> None:
        for index, stored in enumerate(self.base):
            if stored.id == reservation.id:
                self.base[index] = reservation
                return
        self.base.append(reservation)

    def get_reservation_by_id(self, id: str) -> ReservationSchema | None:
        for stored in self.base:
            if stored.id == id:
                return stored
