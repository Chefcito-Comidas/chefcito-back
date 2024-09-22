from typing import Optional
from pydantic import BaseModel

from src.model.reservations.reservation import Canceled, Expired, Reservation
from src.model.reservations.update import Update


class Point(BaseModel):
    total: int
    user: str


    @classmethod
    def is_negative(cls, reservation: Reservation) -> bool:
        r_status = reservation.get_status()
        return r_status == Canceled().get_status() or r_status == Expired().get_status()

    @classmethod
    def __get_negative_points(cls, reservation: Reservation, update: Optional[Update]) -> int:
        if not update is None and update.user == f"user/{reservation.venue}" and reservation.get_status() == Canceled().get_status():
            return 0
        return -50
    @classmethod
    def from_reservation(cls, reservation: Reservation, update: Optional[Update] = None) -> 'Point':
        if cls.is_negative(reservation):
            return cls(total=cls.__get_negative_points(reservation, update), user=reservation.user)
        return cls(total=50, user=reservation.user)