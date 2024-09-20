import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel
from src.model.opinions.opinion import Opinion
from src.model.opinions.opinion_query import OpinionQuery
from src.model.opinions.provider import OpinionsProvider
from src.model.reservations.data.base import ReservationsBase
from src.model.reservations.data.query import get_builder
from src.model.reservations.reservation import Reservation


class ReservationQueryResponse(BaseModel):
    result: List[Reservation]
    opinions: Dict[str, Opinion]
    total: int

class ReservationQuery(BaseModel):
    
    limit: int = 10
    start: int = 0
    status: Optional[List[str]] = None
    id: Optional[str] = None
    user: Optional[str] = None
    venue: Optional[str] = None
    from_time: Optional[datetime] = None
    to_time: Optional[datetime] = None
    people: Optional[Tuple[int, int]] = None
    
    def change_user(self, user: str):
        self.user = f"user/{user}"

    async def __search_opinions(self, reservations: List[Reservation], opinions: OpinionsProvider) -> Dict[str, Opinion]:
        final = {}
        promises = list(
            map(
                lambda x: opinions.query_opinions(OpinionQuery(venue=x.venue, reservation=x.id)),
                reservations 
            )
        )
        for result in promises:
            value = await result
            print(value)
            if isinstance(value, dict) and value['total'] > 0:
                op = value['result'].pop()
                final[op.reservation] = op
            elif value.total > 0:
                op = value.result.pop()
                final[op.reservation] = op

        return final 

    async def query(self, db: ReservationsBase, opinions: OpinionsProvider) -> ReservationQueryResponse: 
        builder = get_builder(db)
        time = (self.from_time, self.to_time) if self.from_time != None and self.to_time != None else None
        result = await builder.get(self.id, self.user, self.status, self.venue, time, self.people, self.limit, self.start)
        reservations = [Reservation.from_schema(value) for value in result.result]
        opinions_result = await self.__search_opinions(reservations, opinions)
        return ReservationQueryResponse(result=reservations, 
                                        opinions=opinions_result,
                                        total=result.total)
