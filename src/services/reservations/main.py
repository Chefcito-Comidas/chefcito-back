from typing import Annotated, List, Tuple
from fastapi import Body, FastAPI, Path, Query, Response
from pydantic_settings import BaseSettings

from src.model.commons.error import Error
from src.model.reservations.data.base import MockBase, RelBase
from src.model.reservations.reservation import CreateInfo, Reservation
from src.model.reservations.reservationQuery import ReservationQuery
from src.model.reservations.service import LocalReservationsProvider, ReservationsProvider, ReservationsService
from src.model.reservations.update import Update

class Settings(BaseSettings):
    db_string: str = "database_conn_string"

settings = Settings()

app = FastAPI()
database =  RelBase(settings.db_string) 
service = ReservationsService(LocalReservationsProvider(database))


@app.post("/reservations")
async def create_reservation(reservation: Annotated[CreateInfo, Body()], response: Response) -> Reservation | Error:
    return await service.create_reservation(reservation, response)

@app.put("/reservations/{reservation}")
async def update_reservation(reservation: Annotated[str, Path()], update: Annotated[Update, Body()], response: Response) -> Reservation | Error:
    print(reservation)
    return await service.update_reservation(reservation, update, response)

@app.delete("/reservations/{reservation}")
async def delete_reservation(reservation: Annotated[str, Path()]) -> None:
    return await service.delete_reservation(reservation)

@app.get("/reservations/")
async def get_reservations(response: Response,
                           id: str = Query(default=None),
                           user: str = Query(default=None),
                           venue: str = Query(default=None),
                           from_time: str = Query(default=None),
                           to_time: str = Query(default=None),
                           from_people: int = Query(default=None),
                           to_people: int = Query(default=None),
                           ) -> List[Reservation] | Error:
    print("Here I Amo")
    query = ReservationQuery(
            id=id,
            user=user,
            venue=venue,
            time=(from_time, to_time) if from_time != None and to_time != None else None,
            people=(from_people, to_people) if from_people != None and to_people != None else None
            )
    return await service.get_reservations(query, response)
