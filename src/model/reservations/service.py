from typing import List
from fastapi import Response, status

from src.model.commons.error import Error
from src.model.reservations.reservation import Reservation
from src.model.reservations.update import Update
from src.model.reservations.reservationQuery import ReservationQuery


class ReservationsProvider:
    
    async def create_reservation(self, reservation: Reservation) -> Reservation:
        raise Exception("Interface method should not be called")

    async def update_reservation(self, reservation: Reservation, reservation_update: Update) -> Reservation:
        raise Exception("Interface method should not be called")
    
    async def get_reservations(self, query: ReservationQuery) -> List[Reservation]:
        raise Exception("Interface method should not be called")
    

class ReservationsService:

    def __init__(self, provider: ReservationsProvider):
        self.provider = provider

    
    async def create_reservation(self, reservation: Reservation, response: Response) -> Reservation | Error:
        try:
           return await self.provider.create_reservation(reservation)
        except Exception as e:
           response.status_code = status.HTTP_400_BAD_REQUEST
           return Error.from_exception(e)
    
    async def update_reservation(self, reservation: Reservation, update: Update, response: Response) -> Reservation | Error:
        try:
           return await self.provider.update_reservation(reservation, update)
        except Exception as e:
           response.status_code = status.HTTP_400_BAD_REQUEST
           return Error.from_exception(e)
    
    async def get_reservations(self, query: ReservationQuery, response: Response) -> List[Reservation] | Error:
        try:
           return await self.provider.get_reservations(query)
        except Exception as e:
           response.status_code = status.HTTP_400_BAD_REQUEST
           return Error.from_exception(e)
    


class HttpReservationsProvider(ReservationsProvider):
    pass

class LocalReservationsProvider(ReservationsProvider):
    pass

