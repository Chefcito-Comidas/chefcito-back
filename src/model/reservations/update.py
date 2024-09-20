from datetime import datetime
from typing import Optional
from pydantic import BaseModel

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

    async def modify(self, reservation: Reservation, stats: StatsProvider) -> Reservation:

        if self.cancel:
            print("==> Canceling reservation")
            reservation.cancel()

        if not self.advance_forward is None:
            print("==> Advancing reservation")
            reservation.advance(self.advance_forward, self.user)

        if self.time:
            print("==> Changing reservation time")
            reservation.time = self.time
            reservation.modified()

        if self.people:
            print("==> Changing reservation people")
            reservation.people = self.people
            reservation.modified()

        if reservation.notifiable():
            print("==> Notifying stats service")
            await stats.update(StatsUpdate.from_reservation(reservation))

        return reservation
