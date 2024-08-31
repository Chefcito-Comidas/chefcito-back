from datetime import datetime
from typing import List, Optional, Tuple
from pydantic import BaseModel
from src.model.reservations.data.base import ReservationsBase
from src.model.reservations.data.query import get_builder
from src.model.reservations.reservation import Reservation


class ReservationQueryResponse(BaseModel):
    result: List[Reservation]
    total: int

class ReservationQuery(BaseModel):
    
    limit: int = 10
    start: int = 0
    status: Optional[List[str]] = None
    id: Optional[str] = None
    user: Optional[str] = None
    venue: Optional[str] = None
    from_time: Optional[datetime] = None
    to_time: Optional[datetime] = None
    people: Optional[Tuple[int, int]] = None
    
    def change_user(self, user: str):
        self.user = f"user/{user}"

    def query(self, db: ReservationsBase) -> ReservationQueryResponse: 
        builder = get_builder(db)
        time = (self.from_time, self.to_time) if self.from_time != None and self.to_time != None else None
        result = builder.get(self.id, self.user, self.status, self.venue, time, self.people, self.limit, self.start)
        reservations = [Reservation.from_schema(value) for value in result.result]
        return ReservationQueryResponse(result=reservations, total=result.total)
