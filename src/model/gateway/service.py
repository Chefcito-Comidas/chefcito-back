from typing import Annotated, List
from fastapi import Body, Response, status
from src.model.commons.caller import post, recover_json_data
from src.model.commons.error import Error
from fastapi.security import HTTPAuthorizationCredentials
from src.model.reservations.reservation import Reservation
from src.model.reservations.reservationQuery import ReservationQuery
from src.model.reservations.service import ReservationsProvider, ReservationsService
from src.model.reservations.update import Update
from src.model.users.service import UsersProvider, UsersService
from src.model.users.user_data import UserData, UserToken
import src.model.gateway.reservations_stubs as r_stubs 

class GatewayService:
    
    def __init__(self, users: UsersProvider, reservations: ReservationsService):
        self.users = users 
        self.reservations = reservations


    async def sign_in(self, credentials: Annotated[HTTPAuthorizationCredentials, None],
                  response: Response) -> UserData | Error:
        """
        Gets data from the respective user
        """
        try:
            data = UserToken(id_token=credentials.credentials)
            return await self.users.get_data(data)
        except Exception as e:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return Error.from_exception(e, "/users")



    async def sign_up(self, credentials: Annotated[HTTPAuthorizationCredentials, None],
                  user_type: Annotated[str, Body()]) -> UserData | Error:
        """
        Adds a new user to the system
        """
        try:
            data= UserToken(id_token=credentials.credentials)
            return await self.users.sign_up(user_type, data) 
        except Exception as e:
            return Error.from_exception(e, endpoint="/users")
    
    async def create_reservation(self,credentials: Annotated[HTTPAuthorizationCredentials, None], reservation: r_stubs.CreateInfo, response: Response) -> Reservation | Error:
        user = await self.users.get_data(UserToken(id_token=credentials.credentials))
        return await self.reservations.create_reservation(reservation.with_user(user.localid), response)

    async def update_reservation(self,credentials: Annotated[HTTPAuthorizationCredentials, None], reservation_id: str, reservation_update: r_stubs.Update, response: Response) -> Reservation | Error:
        user = await self.users.get_data(UserToken(id_token=credentials.credentials))
        update = reservation_update.with_user(user.localid) 
        return await self.reservations.update_reservation(reservation_id, update, response)

    async def get_reservations(self,credentials: Annotated[HTTPAuthorizationCredentials, None], reservation_query: r_stubs.ReservationQuery, response: Response) -> List[Reservation] | Error:
        user = await self.users.get_data(UserToken(id_token=credentials.credentials))
        r_query = reservation_query.with_user(user.localid)
        return await self.reservations.get_reservations(r_query, response)

    async def delete_reservation(self,credentials: Annotated[HTTPAuthorizationCredentials, None], reservation_id: str, response: Response) -> None:
        return await self.reservations.delete_reservation(reservation_id)
