from pydantic import BaseModel
from src.model.venues.data.base import VenuesBase
from src.model.venues.data.query import get_builder
from src.model.venues.venue import Venue
from typing import List, Optional, Tuple


class VenueQuery(BaseModel):

    id: Optional[str] = None
    name: Optional[str] = None
    location: Optional[str] = None
    capacity: Optional[int] = None 
   

    def query(self, db: VenuesBase) -> List[Venue]:
        builder = get_builder(db) 
        result = builder.get(self.id, self.name, self.location, self.capacity)

        return [Venue.from_schema(value) for value in result]