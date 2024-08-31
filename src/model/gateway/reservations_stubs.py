
from datetime import datetime
from typing import List, Optional, Tuple
from pydantic import BaseModel
import src.model.reservations.reservation as r 
import src.model.reservations.update as update
import src.model.reservations.reservationQuery as query


class CreateInfo(BaseModel):
    venue: str
    time: datetime 
    people: int

    def with_user(self, user: str) -> r.CreateInfo:
        info = r.CreateInfo(user="",venue=self.venue, time=self.time, people=self.people)
        info.change_user(user)
        return info

class Update(BaseModel):
    advance_forward: Optional[bool] = None
    cancel: bool = False
    time: Optional[datetime] = None 
    people: Optional[int] = None 

    def with_user(self, user: str) -> update.Update:
       value = update.Update(
               user="",
               advance_forward=self.advance_forward,
               cancel=self.cancel,
               time=self.time,
               people=self.people
               )
       value.change_user(user)
       return value

class ReservationQuery(BaseModel):
    
    limit: int = 10
    start: int = 0
    status: Optional[List[str]] = None
    id: Optional[str] = None
    venue: Optional[str] = None
    from_time: Optional[datetime] = None 
    to_time: Optional[datetime] = None
    people: Optional[Tuple[int, int]] = None

    def with_user(self, user: str) -> query.ReservationQuery:
        value = query.ReservationQuery(
                limit=self.limit,
                start=self.start,
                status=self.status,
                id=self.id,
                venue=self.venue,
                from_time=self.from_time,
                to_time=self.to_time,
                people=self.people
                )
        value.change_user(user)
        return value
