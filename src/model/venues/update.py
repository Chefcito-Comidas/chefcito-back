from typing import Optional
from pydantic import BaseModel

from src.model.venues.venue import Venue


class Update(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    capacity: Optional[int] = None
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

        return venue
