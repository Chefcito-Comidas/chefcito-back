from pydantic import BaseModel
from src.model.users.permissions.base import Database
from src.model.users.user_data import UserData, UserToken, recover_data 
from src.model.users.firebase.api_instance import FirebaseAuth

class AuthRequest(UserToken):
    endpoint: str
    
    async def is_allowed(self, firebase: FirebaseAuth, db: Database) -> bool:
        """
        Returns if the user is allowed to call a certain endpoint
        """
        data = await self.get_data(firebase)
        return data.allowed_to(self.endpoint, db)
