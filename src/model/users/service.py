from typing import Annotated, Any, Dict, Self
from fastapi import Body, Query, status, Response
from src.model.commons.caller import post, recover_json_data
from src.model.commons.error import Error
from src.model.communications.service import CommunicationProvider
from src.model.users.auth_request import AuthRequest
from src.model.users.firebase.api_instance import FirebaseAuth
from src.model.users.permissions.base import Database
from src.model.users.user_data import UserData, UserToken
import src.model.communications.user as c


class UsersProvider:
    
    async def sign_up(self, user_type: str, token: Annotated[UserToken, Body()]) -> UserData:
        raise Exception("Interface method should not be called")

    async def get_data(self, auth: Annotated[UserToken, Body()]) -> UserData:
        raise Exception("Interface method should not be called")

    async def is_allowed(self, auth: Annotated[AuthRequest, Body()]) -> int:
        raise Exception("Interface method should not be called")

class HttpUsersProvider(UsersProvider):
    
    def __init__(self, users_host: str) -> None:
        self.host = users_host 
    
    async def sign_up(self, user_type: str, token: Annotated[UserToken, Body()]) -> UserData:
        endpoint = f"{self.host}/users/signup/{user_type}"
        users_response = await post(endpoint, body=token.model_dump())
        return UserData(**await recover_json_data(users_response))
    
    async def get_data(self, auth: Annotated[UserToken, Body()]) -> UserData:
        endpoint = f"{self.host}/users"
        users_response = await post(endpoint, body=auth.model_dump())
        content = users_response.headers.get('content-type', 'invalid')
        if 'json' not in content:
            raise Exception("Invalid response from users") 
        try:
            return UserData(**await recover_json_data(users_response))
        except:
            raise Exception("Could not recover user data")

    async def is_allowed(self, auth: Annotated[AuthRequest, Body()]) -> int:
        endpoint = f"{self.host}/users/permissions"
        users_response = await post(endpoint, body=auth.model_dump())
        return users_response.status

class LocalUsersProvider(UsersProvider):
    
    def __init__(self, authentication: FirebaseAuth, database: Database, communications: CommunicationProvider) -> None:
        self.authentication = authentication
        self.database = database
        self.communications = communications
    
    async def sign_up(self, user_type: str, token: Annotated[UserToken, Body()]) -> UserData:
        user = await token.get_data(self.authentication, self.database)
        user.insert_into(user_type, self.database)
        
        await self.communications.store_user(c.User(localid=user.localid, number=user.phone_number))
        return user

    async def get_data(self, auth: Annotated[UserToken, Body()]) -> UserData:
        """ 
        Returns all data from the user, including its type
        """
        return await auth.get_data(self.authentication, self.database) 
    
    async def is_allowed(self, auth: Annotated[AuthRequest, Body()]) -> int:
        return status.HTTP_200_OK if await auth.is_allowed(self.authentication, self.database) \
                    else status.HTTP_403_FORBIDDEN

class UsersService:

    def __init__(self, provider: UsersProvider) -> None:
        self.provider = provider

    async def sign_up(self, user_type: str, token: Annotated[UserToken, Body()], response: Response) -> UserData | Error:
        """
        Recieve the token, get the user data for the token and add it
        to the database
        """
        try:
           return await self.provider.sign_up(user_type, token) 
        except Exception as e:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return Error.from_exception(e, endpoint="/signup") 
    
    async def get_data(self, auth: Annotated[UserToken, Body()], response: Response) -> UserData | Error:
        """ 
        Returns all data from the user, including its type
        """
        try:
            return await self.provider.get_data(auth) 
        except Exception as e:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return Error.from_exception(e, endpoint="/users") 
    
    async def is_allowed(self, auth: Annotated[AuthRequest, Body()], response: Response) -> None | Error:
        """
        Checks if the user is allowed or not to access a certain endpoint
        """
        try:
            response.status_code = await self.provider.is_allowed(auth) 
        except Exception as e:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return Error.from_exception(e, endpoint="/permissions")


