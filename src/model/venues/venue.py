from pydantic import BaseModel
from src.model.venues.data.schema import VenueSchema
from typing import Self
from typing import List
from src.model.venues.data.base import VenuesBase
import datetime

def create_venue(name: str, location: str, capacity: int, logo: str, pictures: List[str], slots: List[datetime.datetime]) -> 'Venue':
    return Venue(id="",
                 name=name, 
                 location=location, 
                 capacity=capacity,
                 logo=logo,
                 pictures=pictures,
                 slots=slots,
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


class CreateInfo(BaseModel):
    id: str
    name: str
    location: str
    capacity: int
    logo: str
    pictures: List[str]
    slots: List[datetime.datetime]

    def into_venue(self) -> 'Venue':
        return Venue(id=self.id, 
                     name=self.name, 
                     location=self.location, 
                     capacity=self.capacity, 
                     logo=self.logo, 
                     pictures=self.pictures, 
                     slots=self.slots,
                     status=Available()) 


class Venue(BaseModel):

    id: str
    name: str
    location: str
    capacity: int
    logo: str
    pictures: List[str]
    slots: List[datetime.datetime]
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
    
    def persistance(self) -> VenueSchema:
        if not self.id:
            schema = VenueSchema.create(
                    self.name,
                    self.location,
                    self.capacity,
                    self.logo, 
                    self.pictures, 
                    self.slots,
                    self.status.get_status()
                    )
            self.id = schema.id.__str__()
            return schema
        else:
            return VenueSchema(
                    id=self.id,
                    name=self.name,
                    location=self.location,
                    capacity=self.capacity,
                    logo=self.logo, 
                    pictures=self.pictures, 
                    slots=self.slots,
                    status=self.status.get_status()
                    )

    @staticmethod
    def delete(id: str, database: VenuesBase) -> None:
        return database.delete_venue(id)
    
    @classmethod
    def from_schema(cls, schema: VenueSchema) -> Self:
        return cls(id=schema.id.__str__(),
                   name=schema.name,
                   location=schema.location,
                   capacity=schema.capacity,
                   logo=schema.logo, 
                   pictures=schema.pictures, 
                   slots=schema.slots,
                   status=VenueStatus(status=schema.status)
                   )
