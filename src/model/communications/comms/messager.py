from typing import Any, Dict, List
from src.model.communications.message import Message
from twilio.rest import Client
from twilio.http.async_http_client import AsyncTwilioHttpClient

class CommunicationsMessager():

    async def send_message(self, message: Message, to: str) -> None:
        raise Exception("Interface method should not be called")


class MockedCommunicationsMessager(CommunicationsMessager):
    
    def __init__(self):
        self.messages: List[Dict[str, Any]] = []

    async def send_message(self, message: Message, to: str) -> None:
        new_message = {
            'message': message,
            'to': to
        }
        self.messages.append(new_message)

class TwilioCommunicationsMessager(CommunicationsMessager):

    def __init__(self, account_sid: str, auth_token: str):
        self.client = Client(account_sid, auth_token, http_client=AsyncTwilioHttpClient())

    async def send_message(self, message: Message, to: str) -> None:
        await self.client.messages.create_async(
            to=to,
            body=message.message            
        ) 
     