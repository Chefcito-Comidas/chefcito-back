from datetime import datetime
from typing import Optional, Self
from pydantic import BaseModel

from src.model.reservations.data.base import ReservationsBase
from src.model.reservations.data.schema import ReservationSchema


def create_reservation(user: str, venue: str, time: datetime, people: int) -> 'Reservation':
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

    def advance(self, forward: bool = True) -> 'ReservationStatus':
        return self

    def status_message(self) -> str:
        return "Estado de reserva"

class Uncomfirmed(ReservationStatus):

    def __init__(self):
        super().__init__(status="Uncomfirmed")

    def advance(self, forward: bool = True) -> ReservationStatus:
        if not forward:
            return Canceled() 
        return Accepted()
    
    def status_message(self) -> str:
        return "La reserva aun no esta confirmada"

class Canceled(ReservationStatus):

    def __init__(self):
        super().__init__(status="Canceled")

    def status_message(self) -> str:
        return "Tu reserva a sido cancelada."

class Accepted(ReservationStatus):

    def __init__(self):
        super().__init__(status="Accepted")

    def advance(self, forward: bool = True) -> ReservationStatus:
        if not forward:
            return Expired()
        return Assisted()
    
    def status_message(self) -> str:
        return "La reserva fue aceptada por el local!"

class Assisted(ReservationStatus):
    def __init__(self):
        super().__init__(status="Assited")

    def status_message(self) -> str:
        return "Esperamos que disfrutes tu experiencia ! No te olvides de dejar una reseña luego."

class Expired(ReservationStatus):
    def __init__(self):
        super().__init__(status="Expired")

    def status_message(self) -> str:
        return "Tu reserva a expirado!"

class CreateInfo(BaseModel):
    user: str
    venue: str
    time: datetime 
    people: int

    def into_reservation(self) -> 'Reservation':
        return create_reservation(self.user, self.venue, self.time, self.people) 

    def change_user(self, new_user: str):
        self.user = f"user/{new_user}"

class Reservation(BaseModel):
    
    id: str
    user: str
    venue: str
    time: datetime
    people: int
    status: ReservationStatus

    def get_status(self) -> str:
        return self.status.get_status()

    def modified(self):
        self.status = Uncomfirmed()

    def cancel(self):
        self.status = Canceled()

    def advance(self, forward: bool, who: str):
        if self.status.get_status() == Uncomfirmed().get_status() and forward and who == self.venue:
            self.status = self.status.advance(forward=forward)
        elif self.status.get_status() != Uncomfirmed().get_status() or not forward:
            self.status = self.status.advance(forward=forward)

    def persistance(self) -> ReservationSchema:
        if not self.id:
            schema = ReservationSchema.create(
                    self.user,
                    self.venue,
                    self.time,
                    self.people,
                    self.status.get_status()
                    )
            self.id = schema.id.__str__()
            return schema
            
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
        return cls(id=schema.id.__str__(),
                   user=schema.user,
                   venue=schema.venue,
                   time=schema.time,
                   people=schema.people,
                   status=ReservationStatus(status=schema.status)
                   )

    def change_user(self, new_user: str):
        self.user = f"user/{new_user}"
