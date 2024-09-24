from pydantic import BaseModel

from src.model.reservations.reservation import Canceled, Expired, Reservation


class Point(BaseModel):
    total: int
    user: str


    @classmethod
    def is_negative(cls, reservation: Reservation) -> bool:
        r_status = reservation.get_status()
        return r_status == Canceled().get_status() or r_status == Expired().get_status()

    @classmethod
    def __get_negative_points(cls, reservation: Reservation, updater: str) -> int:
        if updater == f"user/{reservation.venue}" and reservation.get_status() == Canceled().get_status():
            return 0
        return -50
    @classmethod
    def from_reservation(cls, reservation: Reservation, updater: str = "") -> 'Point':
        if cls.is_negative(reservation):
            return cls(total=cls.__get_negative_points(reservation, updater), user=reservation.user)
        return cls(total=50, user=reservation.user)
    
    @classmethod
    def from_opinion(cls, reservation: Reservation) -> 'Point':
        return cls.from_reservation(reservation, "")
