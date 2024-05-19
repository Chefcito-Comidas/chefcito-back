from typing import Dict, Any
import requests as r

class FirebaseAuth():
   
    def get_data(self, token: str) -> Dict[str, str]:
        """
        Calls the API with the given token and returns the user data.
        If the token is invalid, then raises an exception
        """
        raise Exception("Interface method should not be called") 
    
    def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """
        Calls Firebase using the email and password provided by the user
        """
        raise Exception("Interface method should not be called")

class FirebaseClient(FirebaseAuth):
    
    host: str = "https://identitytoolkit.googleapis.com"

    def __init__(self, key: str):
        self.api_key = key

    def get_data(self, token: str) -> Dict[str, str]:
        endpoint = self.host + "/v1/accounts:lookup"
        response = r.post(endpoint, data={"idToken": token}, params={"key": self.api_key})
        if response.status_code != r.codes.ok:
            raise Exception("Invalid token")
        return response.json()['users'][0]
    
    def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        endpoint = self.host + "/v1/accounts:signInWithPassword"
        response = r.post(endpoint, 
                          data={"email": email, "password": password, "returnSecureToken": True},
                          params={"key": self.api_key})
        if response.status_code != r.codes.ok:
            raise Exception("Invalid token")
        return response.json()

class FirebaseMock(FirebaseAuth):
    
    def __init__(self, maped_responses: Dict[str, Dict[str, str]]):
        self.responses = maped_responses

    def get_data(self, token: str) -> Dict[str, str]:
        response = self.responses.get(token) 
        if not response:
            raise Exception("Invalid token")
        return response

