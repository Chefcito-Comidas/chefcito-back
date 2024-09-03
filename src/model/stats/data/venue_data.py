from typing import Annotated
from beanie import Document, Indexed

from src.model.stats.venue_data import VenueStatData


class VenueDataDocument(Document):
    venue: Annotated[str, Indexed()]
    total: int
    canceled: int
    expired: int
    
    
    def into_stat_data(self) -> VenueStatData:
        if self.total == 0:
            return VenueStatData(venue=self.venue, total=0, canceled=0, expired=0, people=0)
        
        return VenueStatData(
            venue=self.venue,
            total=self.total,
            canceled=round(self.canceled / self.total, 2),
            expired=round(self.expired/self.total, 2),
            people=0
        )

    def update_from(self, stat: VenueStatData):
        self.total = stat.total
        self.canceled = round(stat.total * stat.canceled)
        self.expired = round(stat.expired * stat.total)