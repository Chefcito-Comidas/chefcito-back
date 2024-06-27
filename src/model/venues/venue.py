from pydantic import BaseModel

def create_venue(name: str, location: str, capacity: int) -> 'Venue':
    return Venue(name=name, 
                 location=location, 
                 capacity=capacity,
                 status=Available())

class VenueStatus(BaseModel):

    status: str

    def get_status(self) -> str:
        return self.status

class Available(VenueStatus):

    def __init__(self):
        super().__init__(status="Available")

class Occupied(VenueStatus):

    def __init__(self):
        super().__init__(status="Occupied")

class Closed(VenueStatus):

    def __init__(self):
        super().__init__(status="Closed")

class Unconfirmed(VenueStatus):

    def __init__(self):
        super().__init__(status="Unconfirmed")

class Venue(BaseModel):

    name: str
    location: str
    capacity: int
    status: VenueStatus

    def get_status(self) -> str:
        return self.status.get_status()

    def open(self):
        self.status = Available()

    def occupy(self):
        self.status = Occupied()

    def close(self):
        self.status = Closed()

    def unconfirm(self):
        self.status = Unconfirmed()
