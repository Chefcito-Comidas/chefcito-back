from typing import List, Optional, Tuple
from pydantic import BaseModel
from src.model.reservations.data.base import ReservationsBase
from src.model.reservations.data.query import get_builder
from src.model.reservations.reservation import Reservation


class ReservationQuery(BaseModel):
    
    limit: int = 10
    start: int = 0
    id: Optional[str] = None
    user: Optional[str] = None
    venue: Optional[str] = None
    time: Optional[Tuple[str, str]] = None # TODO: Need to enforce datetime for this
    people: Optional[Tuple[int, int]] = None
    
    def change_user(self, user: str):
        self.user = f"user/{user}"

    def query(self, db: ReservationsBase) -> List[Reservation]:
        builder = get_builder(db) 
        result = builder.get(self.id, self.user, self.venue, self.time, self.people, self.limit, self.start)
        return [Reservation.from_schema(value) for value in result]
