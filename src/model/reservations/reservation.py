from pydantic import BaseModel


def create_reservation(user: str, venue: str, time: str, people: int) -> 'Reservation':
    return Reservation(user=user, 
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

    


