from typing import Annotated, Dict
from beanie import Document, Indexed
from pydantic import BaseModel

from src.model.stats.venue_data import VenueMeanPerDay, VenueMeanPerTurn, VenueStatData


class VenueMeanPerDayDocument(BaseModel):
    means: Dict[int, int]

    def to_days(self) -> VenueMeanPerDay:
        return VenueMeanPerDay(means=self.means)

class VenueMeanPerTurnDocument(BaseModel):
    turns: Dict[str, int]

    def to_turns(self) -> VenueMeanPerTurn:
        return VenueMeanPerTurn(turns=self.turns)

class VenueDataDocument(Document):
    venue: Annotated[str, Indexed()]
    total: int
    canceled: int
    expired: int
    people: int
    means: VenueMeanPerDayDocument
    turns: VenueMeanPerTurnDocument


    @classmethod
    def new_document(cls, venue: str) -> 'VenueDataDocument':
        return cls(
            venue=venue,
            total=0,
            canceled=0,
            expired=0,
            people=0,
            means=VenueMeanPerDayDocument(means={}),
            turns=VenueMeanPerTurnDocument(turns={})
        )

    def into_stat_data(self) -> VenueStatData:
        if self.total == 0:
            return VenueStatData(venue=self.venue, total=0, canceled=0, expired=0, people=0)

        return VenueStatData(
            venue=self.venue,
            total=self.total,
            canceled=round(self.canceled / self.total, 2),
            expired=round(self.expired/self.total, 2),
            people=self.people,
            days=self.means.to_days(),
            turns=self.turns.to_turns()
        )

    def update_from(self, stat: VenueStatData):
        self.total = stat.total
        self.canceled = round(stat.total * stat.canceled)
        self.expired = round(stat.expired * stat.total)
        self.people = round(stat.people)
        self.means = VenueMeanPerDayDocument(means=stat.days.means)
        self.turns = VenueMeanPerTurnDocument(turns=stat.turns.turns)
