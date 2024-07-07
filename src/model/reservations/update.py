from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from src.model.reservations.reservation import Reservation


class Update(BaseModel):
    user: str 
    accept: Optional[bool] = False
    cancel: Optional[bool] = False 
    time: Optional[datetime] = None 
    people: Optional[int] = None 
    
    def change_user(self, new_user: str):
        self.user = f"user/{new_user}"

    def modify(self, reservation: Reservation) -> Reservation:
        
        if self.cancel:
            reservation.reject()
            return reservation

        if self.accept and self.user == reservation.venue:
            reservation.accept()
            return reservation

        if self.time:
            reservation.time = self.time
            reservation.modified()

        if self.people:
            reservation.people = self.people
            reservation.modified()

        return reservation
