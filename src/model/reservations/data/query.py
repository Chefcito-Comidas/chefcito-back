from typing import List, Optional, Tuple
from src.model.reservations.data.base import ReservationsBase
from src.model.reservations.data.schema import ReservationSchema


class QueryBuilder: 

    def get_by_id(self, id: str) -> List[ReservationSchema]:
        raise Exception("Interface method should not be called")

    def get(self,
            user: Optional[str],
            venue: Optional[str],
            time: Optional[Tuple[str, str]],
            people: Optional[Tuple[int, int]]) -> List[ReservationSchema]:
        
        raise Exception("Interface method should not be called")

class RelBuilder(QueryBuilder):
    
    def __init__(self, db: ReservationsBase) -> None:
        self.db = db

class MockBuilder(QueryBuilder):

    def __init__(self, db: ReservationsBase) -> None:
        self.db = db

    def get_by_id(self, id: str) -> List[ReservationSchema]:
        return [value for value in [self.db.get_reservation_by_id(id)] if value]

    def get(self, user: Optional[str], venue: Optional[str], time: Optional[Tuple[str, str]], people: Optional[Tuple[int, int]]) -> List[ReservationSchema]:
        return super().get(user, venue, time, people)
