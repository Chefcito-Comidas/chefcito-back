import datetime
from typing import List
from pydantic import BaseModel
import src.model.venues.venue as venues

class CreateInfo(BaseModel):
    name: str
    location: str
    capacity: int
    logo: str
    pictures: List[str]
    slots: List[datetime.datetime]
    characteristics: List[str]
    vacations: List[datetime.datetime]
    reservationLeadTime: int

    def into_create_info(self, id: str) -> venues.CreateInfo:
        return venues.CreateInfo(
            id=id,
            name=self.name,
            location=self.location,
            capacity=self.capacity,
            logo=self.logo,
            pictures=self.pictures,
            slots=self.slots,
            characteristics=self.characteristics,
            vacations=self.vacations,
            reservationLeadTime=self.reservationLeadTime
        )
