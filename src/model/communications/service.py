from src.model.commons import error
from src.model.communications.comms.messager import CommunicationsMessager, MockedCommunicationsMessager
from src.model.communications.data.base import CommunicationsBase
from src.model.communications.message import Message
from src.model.communications.user import User


class CommunicationProvider():

    async def store_user(self, user: User) -> User:
        raise Exception("Interface method should not be called")
    
    async def get_user(self, id: str) -> User | None:
        raise Exception("Interface method should not be called")

    async def send_message(self, message: Message) -> None:
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

    async def send_message(self, message: Message) -> None | error.Error:
        try:
            await self.provider.send_message(message)
        except Exception as e:
            return error.Error.from_exception(e)

class LocalCommunicationProvider(CommunicationProvider):

    def __init__(self, db: CommunicationsBase, messager: CommunicationsMessager = MockedCommunicationsMessager()):
        self.db = db
        self.messager = messager

    async def store_user(self, user: User) -> User:
        await self.db.store_user(user)
        return user

    async def get_user(self, id: str) -> User | None:
        return await self.db.get_user(id)

    async def send_message(self, message: Message) -> None:
        destination = await self.db.get_user(message.user)
        if not destination:
            raise Exception("User does not exists")
        return await self.messager.send_message(message, destination.number) 