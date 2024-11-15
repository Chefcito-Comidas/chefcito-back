from typing import List
from haversine.haversine import math
from pydantic import BaseModel

from src.model.commons.logger import Logger
from src.model.reservations.reservation import Canceled, Expired, Reservation


class PointResponse(BaseModel):
    user: str
    total: int
    level: str



class Point(BaseModel):
    total: int
    user: str


    def get_level(self) -> int:
        """
        if n is the level, it is defined by the minimum n such that
        the following inequality holds
        2^n > (total/100)+1
        """
        #Take the log2 to get just n
        #then return the floor
        level = math.log2((self.total/100) + 1)
        return math.floor(level)

    def into_response(self, levels: List[str] = []) -> PointResponse:
        level = self.get_level()
        level = level if level < len(levels) else len(levels)-1
        return PointResponse(
                user=self.user,
                total=self.total,
                level=levels[level]
                )

    @classmethod
    def is_negative(cls, reservation: Reservation) -> bool:
        r_status = reservation.get_status()
        return r_status == Canceled().get_status() or r_status == Expired().get_status()

    @classmethod
    def __get_negative_points(cls, reservation: Reservation, updater: str) -> int:
        if updater == f"user/{reservation.venue}" and reservation.get_status() == Canceled().get_status():
            Logger.info("Going out through here")
            return 0
        return -50
    @classmethod
    def from_reservation(cls, reservation: Reservation, updater: str = "") -> 'Point':
        if cls.is_negative(reservation):
            return cls(total=cls.__get_negative_points(reservation, updater), user=reservation.user.removeprefix("user/"))
        Logger.info("Adding points")
        return cls(total=50, user=reservation.user.removeprefix("user/"))

    @classmethod
    def from_opinion(cls, reservation: Reservation) -> 'Point':
        return cls.from_reservation(reservation, "")
