from pydantic import BaseModel
from src.model.venues.data.base import VenuesBase
from src.model.venues.data.query import get_builder
from src.model.venues.venue import Venue
from typing import List, Optional, Tuple
import datetime


class VenueDistance(BaseModel):
    venue: Venue
    distance: int

class VenueDistanceQueryResult(BaseModel):
    result: List[VenueDistance]
    total: int

class VenueQueryResult(BaseModel):
    result: List[Venue]
    total: int


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
    characteristics: Optional[List[str]] = None
    features: Optional[List[str]] = None
    vacations: Optional[List[datetime.datetime]] = None
    reservationLeadTime: Optional[int] = None
    menu: Optional[str] = None
   

    def query(self, db: VenuesBase) -> VenueQueryResult:
        builder = get_builder(db) 
        result, total = builder.get(self.id, self.name, self.location, self.capacity, self.logo, self.pictures, self.slots, self.characteristics, self.features, self.vacations, self.reservationLeadTime, self.menu, self.limit, self.start)

        result = [Venue.from_schema(value) for value in result]
        return VenueQueryResult(result=result, total=total)
