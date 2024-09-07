from typing import Annotated, Dict
from beanie import Document, Indexed

from src.model.stats.venue_data import VenueStatData


class VenueMeanPerDayDocument(Document):
    means: Dict[int, int]

class VenueDataDocument(Document):
    venue: Annotated[str, Indexed()]
    total: int
    canceled: int
    expired: int
    people: int
    means: VenueMeanPerDayDocument

    @classmethod
    def new_document(cls, venue: str) -> 'VenueDataDocument':
        return cls(
            venue=venue,
            total=0,
            canceled=0,
            expired=0,
            people=0,
            means=VenueMeanPerDayDocument(means={})
        )
    
    def into_stat_data(self) -> VenueStatData:
        if self.total == 0:
            return VenueStatData(venue=self.venue, total=0, canceled=0, expired=0, people=0)
        
        return VenueStatData(
            venue=self.venue,
            total=self.total,
            canceled=round(self.canceled / self.total, 2),
            expired=round(self.expired/self.total, 2),
            people=round(self.people/self.total, 2)
        )

    def update_from(self, stat: VenueStatData):
        self.total = stat.total
        self.canceled = round(stat.total * stat.canceled)
        self.expired = round(stat.expired * stat.total)