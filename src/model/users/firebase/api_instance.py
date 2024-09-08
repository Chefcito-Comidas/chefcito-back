from typing import Callable, Dict, Any

from fastapi import status
from src.model.commons.caller import HTTPMethod, back_off, post, recover_json_data
import src.model.users.firebase.exceptions as fe
import aiohttp

class FirebaseAuth():
   
    async def get_data(self, token: str) -> Dict[str, str]:
        """
        Calls the API with the given token and returns the user data.
        If the token is invalid, then raises an exception
        """
        raise Exception("Interface method should not be called") 
    
    async def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """
        Calls Firebase using the email and password provided by the user
        """
        raise Exception("Interface method should not be called")

class FirebaseClient(FirebaseAuth):
    
    # TODO: This endpoint should be configurable ? 
    # make it low priority, since we are probably not going to move away from firebase
    host: str = "https://identitytoolkit.googleapis.com"

    def __init__(self, key: str):
        self.api_key = key
    
    async def call_endpoint(self, endpoint: str, data: dict = {}, params: dict = {}) -> aiohttp.ClientResponse:
        endpoint = f"{self.host}{endpoint}"
        response = await post(endpoint, body=data, params=params)
        return response

    def __get_backoff_method(self) -> HTTPMethod:
        async def method(endpoint: str, data: dict = {}, body: dict = {}, params: dict = {}) -> aiohttp.ClientResponse:
            response = await self.call_endpoint(endpoint, data=data, params=params)
            if response.status != status.HTTP_200_OK:
                raise fe.InvalidToken()
            return response
        return method  

    async def get_data(self, token: str) -> Dict[str, str]:
        endpoint = "/v1/accounts:lookup"
        method =  self.__get_backoff_method()
        return (await back_off(method, endpoint, data={"idToken": token}, params={"key": self.api_key}))['users'][0]
    
    async def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        endpoint = "/v1/accounts:signInWithPassword"
        print(self.api_key)
        response = await self.call_endpoint(endpoint, 
                          data={"email": email, "password": password, "returnSecureToken": True},
                          params={"key": self.api_key})
        
        if response.status != status.HTTP_200_OK:
            raise fe.InvalidToken() 
        return await recover_json_data(response)

class FirebaseMock(FirebaseAuth):
    
    def __init__(self, maped_responses: Dict[str, Dict[str, str]]):
        self.responses = maped_responses

    async def get_data(self, token: str) -> Dict[str, str]:
        response = self.responses.get(token) 
        if not response:
            raise fe.InvalidToken() 
        return response

