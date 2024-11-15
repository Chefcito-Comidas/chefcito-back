from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel

from src.model.commons.logger import Logger
from src.model.points.point import Point
from src.model.points.provider import PointsProvider
from src.model.reservations.reservation import Reservation
from src.model.stats.provider import StatsProvider
from src.model.stats.stats_update import StatsUpdate


class Update(BaseModel):
    user: str
    advance_forward: Optional[bool] = None
    cancel: bool = False
    time: Optional[datetime] = None
    people: Optional[int] = None

    def change_user(self, new_user: str):
        self.user = f"user/{new_user}"

    async def modify(self, reservation: Reservation, stats: StatsProvider, points: PointsProvider) -> Reservation:

        if self.cancel:
            reservation.cancel()

        if not self.advance_forward is None:
            reservation.advance(self.advance_forward, self.user)

        if self.time:
            self.time = self.time - timedelta(hours=-3)
            reservation.time = self.time
            reservation.modified()

        if self.people:
            reservation.people = self.people
            reservation.modified()
        Logger.info(f"update: {reservation.status} && {reservation.notifiable()}")
        if reservation.notifiable():
            await stats.update(reservation)
            await points.update_points(Point.from_reservation(reservation, updater=self.user))

        return reservation
