from typing import List, Optional, Tuple
from pydantic import BaseModel
from src.model.reservations.data.query import QueryBuilder
from src.model.reservations.reservation import Reservation


class ReservationQuery(BaseModel):
    
    id: Optional[str] = None
    user: Optional[str] = None
    venue: Optional[str] = None
    time: Optional[Tuple[str, str]] = None # TODO: Need to enforce datetime for this
    people: Optional[Tuple[int, int]] = None

    def query(self, db: QueryBuilder) -> List[Reservation]:
        
        if self.id:
            result = db.get_by_id(self.id)
        else:
            result = db.get(self.user, self.venue, self.time, self.people)

        return [Reservation.from_schema(value) for value in result]
