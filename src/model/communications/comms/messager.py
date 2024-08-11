from typing import Any, Dict, List
from src.model.communications.message import Message


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