from collections.abc import Coroutine
from datetime import datetime
from typing import List, Optional
from beanie.odm.queries.find import FindMany
from pydantic import BaseModel
from src.model.opinions.data.OpinionSchema import OpinionSchema
from src.model.opinions.opinion import Opinion

class OpinionQueryResponse(BaseModel):
    result: List[Opinion]
    total: int

class OpinionQuery(BaseModel):

    venue: Optional[str] = None
    from_date: Optional[datetime] = None  
    to_date: Optional[datetime] = None
    reservation: Optional[str] = None
    limit: int = 10
    start: int =  0
    
    def __base_query(self) -> FindMany[OpinionSchema] | None:
        if not self.venue and (not self.from_date or not self.to_date):
            return None 

        query = OpinionSchema.find() 
        if self.venue:
            query = query.find(OpinionSchema.venue == self.venue)
        if self.reservation:
            query = query.find(OpinionSchema.reservation == self.reservation)
        if self.from_date:
            query = query.find(
                    OpinionSchema.date.__ge__(self.from_date)
                    )
        if self.to_date:
            query = query.find(
                    OpinionSchema.date.__le__(self.to_date)
                    )

        return query


    def query(self) -> FindMany[OpinionSchema] | None:
        query = self.__base_query()
        if query == None:
            return None
        return query.limit(self.limit).skip(self.start)
    
    async def total_query(self) -> int:
       query = self.__base_query()
       if query == None:
           return 0
       return await query.count() 
