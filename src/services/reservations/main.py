from typing import Annotated, List
from fastapi import Body, FastAPI, Response

from src.model.commons.error import Error
from src.model.reservations.reservation import Reservation
from src.model.reservations.reservationQuery import ReservationQuery
from src.model.reservations.service import ReservationsProvider, ReservationsService
from src.model.reservations.update import Update


app = FastAPI()
service = ReservationsService(ReservationsProvider())


@app.post("/reservation")
async def create_reservation(reservation: Annotated[Reservation, Body()], response: Response) -> Reservation | Error:
    return await service.create_reservation(reservation, response)

@app.put("/reservation")
async def update_reservation(reservation: Annotated[Reservation, Body()], update: Annotated[Update, Body()], response: Response) -> Reservation | Error:
    return await service.update_reservation(reservation, update, response)

@app.post("/search")
async def get_reservations(query: Annotated[ReservationQuery, Body()], response: Response) -> List[Reservation] | Error:
    # TODO: add pagination to this particular endpoint
    return await service.get_reservations(query, response)
