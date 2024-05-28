from typing import Annotated
from fastapi import Body, Response, status
from src.model.commons.caller import post, recover_json_data
from src.model.commons.error import Error
from fastapi.security import HTTPAuthorizationCredentials
from src.model.users.user_data import UserData, UserToken



class GatewayService:
    
    def __init__(self, users_host: str = "http://users"):
        self.users = users_host


    async def sign_in(self, credentials: Annotated[HTTPAuthorizationCredentials, None],
                  response: Response) -> UserData | Error:
        """
        Gets data from the respective user
        """
        try:
            data = UserToken(id_token=credentials.credentials)
            users_response = await post(f"{self.users}/users", body=data.model_dump())
            return await recover_json_data(users_response) 
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
            endpoint = f"{self.users}/users/signup/{user_type}"
            users_response = await post(endpoint, body=data.model_dump())
            return await recover_json_data(users_response) 
        except Exception as e:
            return Error.from_exception(e, endpoint="/users")

