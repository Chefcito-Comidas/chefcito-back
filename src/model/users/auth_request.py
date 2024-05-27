from src.model.users.permissions.base import Database
from src.model.users.permissions.schema import User
from src.model.users.user_data import ANONYMOUS_TOKEN, UserData, UserToken, recover_data 
from src.model.users.firebase.api_instance import FirebaseAuth

class AuthRequest(UserToken):
    endpoint: str
    

    async def is_allowed(self, firebase: FirebaseAuth, db: Database) -> bool:
        """
        Returns if the user is allowed to call a certain endpoint
        """
        if self.id_token == ANONYMOUS_TOKEN:
            return await self.__anonymous_allowed(db) 
        data = await self.get_data(firebase)
        return data.allowed_to(self.endpoint, db)

    async def __anonymous_allowed(self, db:Database) -> bool:
        user = User.get_anonymous()
        return db.is_allowed(user, self.endpoint)
