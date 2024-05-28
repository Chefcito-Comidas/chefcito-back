from typing import Annotated, Any, Dict
from fastapi import Body, Query, status, Response
from src.model.commons.error import Error
from src.model.users.auth_request import AuthRequest
from src.model.users.firebase.api_instance import FirebaseAuth
from src.model.users.permissions.base import Database
from src.model.users.user_data import UserData, UserToken


class UsersService:

    def __init__(self, authenthication: FirebaseAuth, database: Database) -> None:
        self.authentication = authenthication
        self.database = database

    async def sign_up(self, user_type: str, token: Annotated[UserToken, Body()], response: Response) -> UserData | Error:
        """
        Recieve the token, get the user data for the token and add it
        to the database
        """
        try:
            user = await token.get_data(self.authentication)
            user.insert_into(user_type, self.database)
            return user
        except Exception as e:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return Error.from_exception(e, endpoint="/signup") 
    
    async def sign_in(self, email: Annotated[str, Query()], password: Annotated[str, Query()]) -> Dict[str, Any]:
        """
        Use this to get the when someone is signing in
        Ask for the token only
        """  
        return await self.authentication.sign_in(email, password) 

    async def get_data(self, auth: Annotated[UserToken, Body()], response: Response) -> UserData | Error:
        """ 
        Returns all data from the user, including its type
        """
        try:
            return await auth.get_data(self.authentication) 
        except Exception as e:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return Error.from_exception(e, endpoint="/users") 
    
    async def is_allowed(self, auth: Annotated[AuthRequest, Body()], response: Response) -> None | Error:
        """
        Checks if the user is allowed or not to access a certain endpoint
        """
        try:
            response.status_code = status.HTTP_200_OK if await auth.is_allowed(self.authentication, self.database) \
                    else status.HTTP_403_FORBIDDEN
        except Exception as e:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return Error.from_exception(e, endpoint="/permissions")


