from src.model.commons import error
from src.model.communications.data.base import CommunicationsBase
from src.model.communications.user import User


class CommunicationProvider():

    async def store_user(self, user: User) -> User:
        raise Exception("Interface method should not be called")
    
    async def get_user(self, id: str) -> User | None:
        raise Exception("Interface method should not be called")

class CommunicationService():

    def __init__(self, provider: CommunicationProvider):
        self.provider = provider

    async def store_user(self, user: User) -> User | error.Error:
        
        try:
            return await self.provider.store_user(user)
        except Exception as e:
            return error.Error.from_exception(e)
        
    async def get_user(self, user_id: str) -> User | error.Error:
        try:
            user = await self.provider.get_user(user_id)
            if not user:
                raise Exception("User not found")
            return user
        except Exception as e:
            return error.Error.from_exception(e)

class LocalCommunicationProvider(CommunicationProvider):

    def __init__(self, db: CommunicationsBase):
        self.db = db

    async def store_user(self, user: User) -> User:
        await self.db.store_user(user)
        return user

    async def get_user(self, id: str) -> User | None:
        return await self.db.get_user(id) 