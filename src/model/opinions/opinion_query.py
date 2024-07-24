from collections.abc import Coroutine
from datetime import datetime
from typing import Optional
from beanie.odm.queries.find import FindMany
from pydantic import BaseModel

from src.model.opinions.data.OpinionSchema import OpinionSchema


class OpinionQuery(BaseModel):

    venue: Optional[str] = None
    from_date: Optional[datetime] = None  
    to_date: Optional[datetime] = None
    limit: int = 10
    start: int =  0


    def query(self) -> FindMany[OpinionSchema] | None:
        if not self.venue and (not self.from_date or not self.to_date):
            return None 

        query = OpinionSchema.find() 
        if self.venue:
            query = query.find(OpinionSchema.venue == self.venue)
        if self.from_date:
            query = query.find(
                    OpinionSchema.date.__ge__(self.from_date)
                    )
        if self.to_date:
            query = query.find(
                    OpinionSchema.date.__le__(self.to_date)
                    )

        return query.limit(self.limit).sort("-date")

