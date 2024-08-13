from typing import Optional
from pydantic import BaseModel
from typing import List
import datetime
from src.model.venues.venue import Venue


class Update(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    capacity: Optional[int] = None
    logo: Optional[str] = None
    pictures: Optional[List[str]] = None
    slots: Optional[List[datetime.datetime]] = None
    characteristics: Optional[List[str]] = None
    vacations: Optional[List[datetime.datetime]] = None
    reservationLeadTime: Optional[int] = None
    open: Optional[bool] = False
    close: Optional[bool] = False
    occupy: Optional[bool] = False  

    def modify(self, venue: Venue) -> Venue:

        if self.close:
            venue.close()
            return venue

        if self.open:
            venue.open()
            return venue

        if self.occupy:
            venue.occupy()
            return venue

        if self.name:
            venue.name = self.name
            venue.unconfirm()

        if self.location:
            venue.location = self.location
            venue.unconfirm()

        if self.capacity:
            venue.capacity = self.capacity
            venue.unconfirm()

        if self.logo:
            venue.logo = self.logo
            venue.unconfirm()
        
        if self.pictures:
            venue.pictures = self.pictures
            venue.unconfirm()

        if self.slots:
            venue.slots = self.slots
            venue.unconfirm()

        if self.characteristics:
            venue.characteristics = self.characteristics
            venue.unconfirm()

        if self.vacations:
            venue.vacations = self.vacations
            venue.unconfirm()
        
        if self.reservationLeadTime:
            venue.reservationLeadTime = self.reservationLeadTime
            venue.unconfirm()
        return venue
