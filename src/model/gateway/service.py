from ast import Dict
from logging import log
import logging
from typing import Annotated, List, Tuple
from fastapi import Body, HTTPException, Response, status
from starlette.status import HTTP_403_FORBIDDEN
from src.model.commons.error import Error
from fastapi.security import HTTPAuthorizationCredentials
from src.model.commons.logger import Logger
from src.model.opinions.opinion import Opinion
from src.model.opinions.opinion_query import OpinionQuery, OpinionQueryResponse
from src.model.reservations.reservation import Reservation
from src.model.reservations.reservationQuery import ReservationQueryResponse
from src.model.reservations.service import  ReservationsService
from src.model.reservations.update import Update
from src.model.stats.user_data import UserStatData
from src.model.stats.venue_data import VenueStatData
from src.model.users.service import UsersProvider
from src.model.users.user_data import UserData, UserToken
import src.model.gateway.reservations_stubs as r_stubs 
from src.model.venues import venue
from src.model.venues.venue import Venue
from src.model.venues.venueQuery import VenueQuery, VenueQueryResult
from src.model.venues.service import VenuesService
from src.model.venues.update import Update      
import src.model.gateway.venues_stubs as v_stubs


class GatewayService:
    
    def __init__(self, users: UsersProvider, reservations: ReservationsService, venues: VenuesService):
        self.users = users 
        self.reservations = reservations
        self.venues = venues


    async def sign_in(self, credentials: Annotated[HTTPAuthorizationCredentials, None],
                  response: Response) -> UserData | Error:
        """
        Gets data from the respective user
        """
        try:
            Logger.info("Signing in new user")
            data = UserToken(id_token=credentials.credentials)
            return await self.users.get_data(data)
        except Exception as e:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return Error.from_exception(e, "/users")



    async def sign_up(self, credentials: Annotated[HTTPAuthorizationCredentials, None],
                  user_type: Annotated[str, Body()],
                  name: str,
                  number: str) -> UserData | Error:
        """
        Adds a new user to the system
        """
        try:
            Logger.info("Signing up new user")
            data= UserToken(id_token=credentials.credentials)
            result = await self.users.sign_up(user_type, data, name, number) 
            Logger.info(f"New user signed up ==> {result.localid}")
            return result
        except Exception as e:
            return Error.from_exception(e, endpoint="/users")
    
    async def __check_user(self,token: Annotated[HTTPAuthorizationCredentials, None], user: str, response: Response) -> bool:
        """
            Returns False if the check does not pass
            That would mean the user is not the same as 
            the token.
            It also sets the response status code as 403 (Forbidden)
        """
        tokens_user = await self.__get_user(token)
        result = tokens_user == user
        if not result:
            response.status_code = HTTP_403_FORBIDDEN
        return result 

    async def __get_user(self, credentials: Annotated[HTTPAuthorizationCredentials, None]) -> str:
        """
            Returns the id of the user in the credentials
        """
        response = await self.users.get_data(UserToken(id_token=credentials.credentials))
        return response.localid

    async def create_venue(self, credentials: Annotated[HTTPAuthorizationCredentials, None], venue: v_stubs.CreateInfo, response: Response) -> Venue | Error:
        Logger.info("Creating new venue")
        id = await self.users.get_data(UserToken(id_token=credentials.credentials)) 
        Logger.info(f"Recovered user ID ==> {id}")
        new_venue = await self.venues.create_venue(venue.into_create_info(id.localid), response)
        Logger.info(f"Venue created with response: {new_venue}")
        return new_venue 

    async def update_venue(self,credentials: Annotated[HTTPAuthorizationCredentials, None], venue_id: str, venue_update: Update, response: Response) -> Venue | Error:
        Logger.info(f"Updating venue ==> {venue_id}")
        if not await self.__check_user(credentials, venue_id, response):
            return Error(description="Invalid user")
        return await self.venues.update_venue(venue_id, venue_update, response)

    async def get_venues(self, venue_query: VenueQuery, response: Response) -> VenueQueryResult | Error:
        Logger.info(f"Querying venues ==> {venue_query}")
        return await self.venues.get_venues(venue_query, response)

    async def get_venues_near_to(self, location: Tuple[str, str], response: Response) -> VenueQueryResult | Error:
        Logger.info(f"Querying venues around ({location[0]}, {location[1]})")
        return await self.venues.get_venues_near_to(location, response)

    async def delete_venue(self, credentials: Annotated[HTTPAuthorizationCredentials, None], venue_id: str, response: Response) -> None:
        Logger.info(f"Deleting venue ==> {venue_id}")
        if not await self.__check_user(credentials, venue_id, response):
            return
        await self.venues.delete_venue(venue_id)

    async def create_reservation(self,credentials: Annotated[HTTPAuthorizationCredentials, None], reservation: r_stubs.CreateInfo, response: Response) -> Reservation | Error:
        Logger.info("Creating new reservation")
        user = await self.__get_user(credentials)
        return await self.reservations.create_reservation(reservation.with_user(user), response)

    async def update_reservation(self,credentials: Annotated[HTTPAuthorizationCredentials, None], reservation_id: str, reservation_update: r_stubs.Update, response: Response) -> Reservation | Error:
        user = await self.__get_user(credentials) 
        Logger.info(f"Updating reservation ==> {reservation_id} for user ==> {user}")
        update = reservation_update.with_user(user) 
        return await self.reservations.update_reservation(reservation_id, update, response)

    async def get_reservations(self,credentials: Annotated[HTTPAuthorizationCredentials, None], reservation_query: r_stubs.ReservationQuery, response: Response) -> ReservationQueryResponse | Error:
        user = await self.__get_user(credentials) 
        Logger.info(f"Querying users ==> {user} reservations")
        r_query = reservation_query.with_user(user)
        return await self.reservations.get_reservations(r_query, response)
    
    async def get_my_venue(self, credentials: Annotated[HTTPAuthorizationCredentials, None], response: Response) -> Venue | Error:
        user = await self.__get_user(credentials)
        venue_query = VenueQuery(id=user)
        result = await self.venues.get_venues(venue_query, response)
        Logger.info("Retrieving venue data for user ==> {user}") 
        try:
            as_result: dict = result  # type: ignore
            if as_result['total'] > 0:
                return as_result['result'].pop()
            return result # type: ignore
        except Exception as e:
            Logger.critical(e)
            return Error.from_exception(Exception("Invalid user")) 
        

    async def delete_reservation(self,credentials: Annotated[HTTPAuthorizationCredentials, None], reservation_id: str, response: Response) -> None:
        Logger.info(f"Deleting reservation {reservation_id}")
        return await self.reservations.delete_reservation(reservation_id)
    
    async def get_history(self, credentials: Annotated[HTTPAuthorizationCredentials, None], limit: int, start: int, venue: bool, response: Response) -> ReservationQueryResponse | Error:
        user = await self.__get_user(credentials)
        venue_id = None
        Logger.info(f"Retrieving reservation history for {"user" if not venue else "venue"} ==> {user}")
        if venue:
            venue_id = user
            user = None
        query = r_stubs.ReservationQuery(venue=venue_id, limit=limit, start=start).with_user('')
        query.user = user
        return await self.reservations.get_reservations(query, response)
        


    async def create_opinion(self, credentials: Annotated[HTTPAuthorizationCredentials, None],
                             opinion: Opinion,
                             response: Response) -> Opinion | Error:
        user = await self.__get_user(credentials)
        Logger.info(f"Creating new opinion ==> {opinion.venue} user ==> {user}")
        return await self.reservations.create_opinion(opinion, user, response)

    async def get_opinions(self,
                               query: OpinionQuery,
                               response: Response) -> OpinionQueryResponse | Error:
        Logger.info(f"Querying reservations ==> {query}")
        return await self.reservations.get_opinions(query, response)

    async def get_user_stats(self, user: str) -> UserStatData:
        try:
            Logger.info(f"Retrieving user ==> {user} stats")
            return await self.reservations.get_user_stats(user)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=e.__str__()
            )
    
    async def get_venue_stats(self, venue: str) -> VenueStatData:
        try:
            Logger.info(f"Retrieving venue ==> {venue} stats")
            return await self.reservations.get_venue_stats(venue)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=e.__str__()
            )
        
