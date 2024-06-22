from typing import Self
from pydantic import BaseModel

from src.model.reservations.data.base import ReservationsBase
from src.model.reservations.data.schema import ReservationSchema


def create_reservation(user: str, venue: str, time: str, people: int) -> 'Reservation':
    return Reservation(id="",
                        user=user, 
                        venue=venue, 
                        time=time, 
                        people=people,
                        status=Uncomfirmed())

class ReservationStatus(BaseModel):

    status: str

    def get_status(self) -> str:
        return self.status

class Uncomfirmed(ReservationStatus):

    def __init__(self):
        super().__init__(status="Uncomfirmed")

class Canceled(ReservationStatus):

    def __init__(self):
        super().__init__(status="Canceled")

class Accepted(ReservationStatus):

    def __init__(self):
        super().__init__(status="Accepted")

class Reservation(BaseModel):
    
    id: str
    user: str
    venue: str
    time: str
    people: int
    status: ReservationStatus

    def get_status(self) -> str:
        return self.status.get_status()

    def modified(self):
        self.status = Uncomfirmed()

    def accept(self):
        self.status = Accepted()

    def reject(self):
        self.status = Canceled() 

    def persistance(self) -> ReservationSchema:
        if not id:
            return ReservationSchema.create(
                    self.user,
                    self.venue,
                    self.time,
                    self.people,
                    self.status.get_status()
                    )
        else:
            return ReservationSchema(
                    id=self.id,
                    user=self.user,
                    venue=self.venue,
                    time=self.time,
                    people=self.people,
                    status=self.status.get_status()
                    )
    
    @staticmethod
    def delete(id: str, database: ReservationsBase) -> None:
        return database.delete_reservation(id)

    @classmethod
    def from_schema(cls, schema: ReservationSchema) -> Self:
        return cls(id=schema.id,
                   user=schema.user,
                   venue=schema.venue,
                   time=schema.time,
                   people=schema.people,
                   status=ReservationStatus(status=schema.status)
                   )


