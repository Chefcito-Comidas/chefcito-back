import json
from fastapi import logger
from src.model.commons import error
from src.model.commons.caller import post
from src.model.communications.comms.messager import CommunicationsMessager, MockedCommunicationsMessager
from src.model.communications.data.base import CommunicationsBase
from src.model.communications.message import Message
from src.model.communications.user import User
from azure.servicebus.aio import ServiceBusClient
from azure.servicebus import ServiceBusMessage

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

class DummyCommunicationProvider(CommunicationProvider):
    async def store_user(self, user: User) -> User:
        return user
    
    async def get_user(self, id: str) -> User | None:
        return None
    
    async def send_message(self, message: Message) -> None:
        logger.logger.info(f"{message.message} sent to {message.user}")

class HttpCommunicationProvider(CommunicationProvider):
    def __init__(self, url: str):
        self.url = url

    async def store_user(self, user: User) -> User:
        endpoint = "/user"
        await post(f"{self.url}{endpoint}", body=user.model_dump())
        return user
    
    async def send_message(self, message: Message) -> None:
        endpoint = "/messages"
        await post(f"{self.url}{endpoint}", body=message.model_dump())

class QueueCommunicationProvider(CommunicationProvider):

    def __init__(self, queue: ServiceBusClient, queuename: str, commsurl: str) -> None:
        self.queue = queue
        self.commsurl = commsurl
        self.queuename = queuename

    async def store_user(self, user: User) -> User:
        provider = HttpCommunicationProvider(self.commsurl)
        await provider.store_user(user)
        return user
    
    async def send_message(self, message: Message) -> None:
        qm = ServiceBusMessage(body=json.dumps(message.model_dump()))
        sender = self.queue.get_queue_sender(queue_name=self.queuename)
        await sender.send_messages(qm)
        return

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