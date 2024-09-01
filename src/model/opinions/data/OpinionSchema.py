from datetime import datetime
from typing import Annotated, Self
from beanie import Document, Indexed
from src.model.opinions.opinion import Opinion

class OpinionSchema(Document):
    
    venue: Annotated[str, Indexed()]
    opinion: str
    reservation: str
    date: datetime

    @classmethod
    def from_opinion(cls, opinion: Opinion) -> Self:
        return cls(venue=opinion.venue,
                   opinion=opinion.opinion,
                   reservation=opinion.reservation,
                   date=opinion.date)
    
    def into_opinion(self) -> Opinion:
        return Opinion(
                venue=self.venue,
                opinion=self.opinion,
                reservation=self.reservation,
                date=self.date
                )