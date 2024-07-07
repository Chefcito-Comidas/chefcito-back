from typing import Annotated, List
from fastapi import Body, Response, status
from src.model.commons.caller import post, recover_json_data
from src.model.commons.error import Error
from fastapi.security import HTTPAuthorizationCredentials
from src.model.users.service import UsersProvider, UsersService
from src.model.users.user_data import UserData, UserToken
from src.model.venues.venue import CreateInfo, Venue
from src.model.venues.venueQuery import VenueQuery
from src.model.venues.service import VenuesProvider, VenuesService
from src.model.venues.update import Update


class GatewayService:
    
    def __init__(self, users: UsersProvider, venues: VenuesService):
        self.users = users 
        self.venues = venues


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
    

    async def create_venue(self, venue: CreateInfo, response: Response) -> Venue | Error:
        return await self.venues.create_venue(venue, response)

    async def update_venue(self, venue_id: str, venue_update: Update, response: Response) -> Venue | Error:
        return await self.venues.update_venue(venue_id, venue_update, response)

    async def get_venues(self, venue_query: VenueQuery, response: Response) -> List[Venue] | Error:
        return await self.venues.get_venues(venue_query, response)

    

