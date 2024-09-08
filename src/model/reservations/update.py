from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from src.model.reservations.reservation import Reservation


class Update(BaseModel):
    user: str 
    advance_forward: Optional[bool] = None
    cancel: bool = False
    time: Optional[datetime] = None 
    people: Optional[int] = None 
    
    def change_user(self, new_user: str):
        self.user = f"user/{new_user}"

    def modify(self, reservation: Reservation) -> Reservation:

        if self.cancel:
            reservation.cancel()

        if self.advance_forward:
            reservation.advance(self.advance_forward, self.user)

        if self.time:
            reservation.time = self.time
            reservation.modified()

        if self.people:
            reservation.people = self.people
            reservation.modified()

        return reservation
