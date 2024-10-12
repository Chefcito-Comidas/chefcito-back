import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel
from src.model.commons import logger
from src.model.commons.logger import Logger
from src.model.opinions.opinion import Opinion
from src.model.opinions.opinion_query import OpinionQuery
from src.model.opinions.provider import OpinionsProvider
from src.model.reservations.data.base import ReservationsBase
from src.model.reservations.data.query import get_builder
from src.model.reservations.reservation import Assisted, Expired, Reservation, ReservationStatus
from src.model.users.service import UsersProvider

class UserData(BaseModel):
    id: str
    name: str
    phone: str
    times_assisted: int
    times_expired: int
    

class ReservationResponse(BaseModel):
    id: str
    user: UserData 
    venue: str
    time: datetime
    people: int
    status: ReservationStatus
    
    def into_reservation(self) -> Reservation:
        return Reservation(
                id=self.id,
                user=self.user.id,
                venue=self.venue,
                time=self.time,
                people=self.people,
                status=self.status
                )


class ReservationQueryResponse(BaseModel):
    result: List[ReservationResponse]
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
            if isinstance(value, dict) and value['total'] > 0:
                op = value['result'].pop()
                final[op['reservation']] = op
            elif not isinstance(value, dict) and value.total > 0:
                op = value.result.pop()
                final[op.reservation] = op

        return final 
    
    async def get_user_data(self, user: str, venue: str, users: UsersProvider, db: ReservationsBase) -> UserData:
        builder = get_builder(db)
        assited = await builder.get(None, user, [Assisted().get_status()], venue, None, None, 10, 0)
        not_assited = await builder.get(None, user, [Expired().get_status()], venue, None, None, 10, 0)
        user_data = await users.get_user(user)
        logger.Logger.info("Hello from here") 
        try:
            return UserData(id=user_data['localid'],
                        name=user_data['name'],
                        phone=user_data['phone_number'],
                        times_expired=not_assited.total,
                        times_assisted=assited.total) 
        except:
            return UserData(id="None", name="None", phone="None", times_expired=0, times_assisted=0)
    async def query(self, db: ReservationsBase, opinions: OpinionsProvider, users: UsersProvider) -> ReservationQueryResponse: 
        builder = get_builder(db)
        time = (self.from_time, self.to_time) if self.from_time != None and self.to_time != None else None
        result = await builder.get(self.id, self.user, self.status, self.venue, time, self.people, self.limit, self.start)
        reservations = [Reservation.from_schema(value) for value in result.result]
        user_datas = [await self.get_user_data(reservation.user, reservation.venue, users, db) for reservation in reservations]
        result_reservations = list(map(
            lambda d: ReservationResponse(user=d[0], id=d[1].id, venue=d[1].venue, time=d[1].time, people=d[1].people, status=d[1].status),
            zip(user_datas, reservations)
            ))
        opinions_result = await self.__search_opinions(reservations, opinions)
        Logger.info(f"Queried reservations and obtained: {reservations}, {opinions_result}")
        return ReservationQueryResponse(result=result_reservations, 
                                        opinions=opinions_result,
                                        total=result.total)
