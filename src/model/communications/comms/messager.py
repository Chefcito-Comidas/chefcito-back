import asyncio
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

    def __init__(self, account_sid: str, auth_token: str, from_number: str = "+13434296384"):
        self.client = Client(account_sid, auth_token)
        self.number = from_number

    def __check_number(self, to: str) -> str:
        return f"+549{to.removeprefix("+549")}"

    async def send_message(self, message: Message, to: str) -> None:
        loop = asyncio.get_event_loop()
        to = self.__check_number(to)
        func = lambda : self.client.messages.create(to=f"whatsapp:{to}",
                                                    from_=f"whatsapp:{self.number}",
                                                    body=message.message)
        await loop.run_in_executor(None, func)
