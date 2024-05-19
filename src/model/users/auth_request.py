from pydantic import BaseModel
from src.model.users.user_data import UserData, recover_data 
from src.model.users.firebase.api_instance import FirebaseAuth

class AuthRequest(BaseModel):
    endpoint: str
    id_token: str
    
    async def get_data(self, firebase: FirebaseAuth) -> 'UserData':
        """
        Tries to recover user data with the firebase authenticator provided
        Raise an exception if the user is invalid
        """
        return recover_data(self.id_token, firebase) 

