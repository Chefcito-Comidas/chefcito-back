from pydantic import BaseModel
from src.model.venues.data.base import VenuesBase
from src.model.venues.data.query import get_builder
from src.model.venues.venue import Venue
from typing import List, Optional, Tuple
import datetime


class VenueQuery(BaseModel):

    limit: int = 10
    start: int = 0
    id: Optional[str] = None
    name: Optional[str] = None
    location: Optional[str] = None
    capacity: Optional[int] = None 
    logo: Optional[str] = None
    pictures: Optional[List[str]] = None
    slots: Optional[List[datetime.datetime]] = None
   

    def query(self, db: VenuesBase) -> List[Venue]:
        builder = get_builder(db) 
        result = builder.get(self.id, self.name, self.location, self.capacity, self.logo, self.pictures, self.slots, self.limit, self.start)

        return [Venue.from_schema(value) for value in result]