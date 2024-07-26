from datetime import datetime
from typing import Annotated, List, Optional, Tuple
from fastapi import Body, FastAPI, Path, Query, Response, status
from pydantic_settings import BaseSettings

from src.model.commons.error import Error
from src.model.opinions.opinion import Opinion
from src.model.opinions.opinion_query import OpinionQuery
from src.model.reservations.data.base import MockBase, RelBase
from src.model.reservations.reservation import CreateInfo, Reservation
from src.model.reservations.reservationQuery import ReservationQuery
from src.model.reservations.service import LocalReservationsProvider, ReservationsProvider, ReservationsService
from src.model.reservations.update import Update
from src.model.venues.service import HttpVenuesProvider
from src.model.opinions.service import HttpOpinionsProvider

class Settings(BaseSettings):
    db_string: str = "database_conn_string"
    venues: str = "http://venues"
    opinions: str = "http://opinions"


settings = Settings()

app = FastAPI()
database =  RelBase(settings.db_string)
venues = HttpVenuesProvider(settings.venues)
opinions = HttpOpinionsProvider(settings.opinions) 
service = ReservationsService(LocalReservationsProvider(database, venues, opinions))


@app.post("/reservations", responses={status.HTTP_400_BAD_REQUEST: {"model": Error}})
async def create_reservation(reservation: Annotated[CreateInfo, Body()], response: Response) -> Reservation | Error:
    return await service.create_reservation(reservation, response)

@app.put("/reservations/{reservation}", responses={status.HTTP_400_BAD_REQUEST: {"model": Error}})
async def update_reservation(reservation: Annotated[str, Path()], update: Annotated[Update, Body()], response: Response) -> Reservation | Error:
    return await service.update_reservation(reservation, update, response)

@app.delete("/reservations/{reservation}", responses={status.HTTP_400_BAD_REQUEST: {"model": Error}})
async def delete_reservation(reservation: Annotated[str, Path()]) -> None:
    return await service.delete_reservation(reservation)

@app.get("/reservations", responses={status.HTTP_400_BAD_REQUEST: {"model": Error}})
async def get_reservations(response: Response,
                           id: str = Query(default=None),
                           user: str = Query(default=None),
                           venue: str = Query(default=None),
                           status: str = Query(default=None),
                           from_time: datetime = Query(default=None),
                           to_time: datetime = Query(default=None),
                           from_people: int = Query(default=None),
                           to_people: int = Query(default=None),
                           limit: int = Query(default=10),
                           start: int = Query(default=0)
                           ) -> List[Reservation] | Error:
    query = ReservationQuery(
            id=id,
            user=user,
            status=status,
            venue=venue,
            from_time=from_time,
            to_time=to_time,
            people=(from_people, to_people) if from_people != None and to_people != None else None,
            limit=limit,
            start=start
            )
    return await service.get_reservations(query, response)

@app.get("/opinions", responses={status.HTTP_400_BAD_REQUEST: {"model": Error}})
async def query_opinions(
                         response: Response,
                         venue: Optional[str] = Query(default=None),
                         from_date: Optional[datetime] = Query(default=None),
                         to_date: Optional[datetime] = Query(default=None),
                         limit: int = Query(default=10),
                         start: int = Query(default=0)):
    query = OpinionQuery(
        venue=venue,
        from_date=from_date,
        to_date=to_date,
        limit=limit,
        start=start
    )
    return await service.get_opinions(query, response)

@app.post("/opinions/{user}", responses={status.HTTP_400_BAD_REQUEST: {"model": Error}})
async def create_opinion(opinion: Annotated[Opinion, Body()], 
                         user: Annotated[str, Path()],
                         response: Response):
    return await service.create_opinion(opinion, user, response)


