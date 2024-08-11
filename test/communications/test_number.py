import asyncio
import pytest

from src.model.communications.comms.messager import MockedCommunicationsMessager
from src.model.communications.data.base import MockedCommunicationsBase
from src.model.communications.service import CommunicationService, LocalCommunicationProvider
from src.model.communications.user import User
from src.model.communications.message import Message

def test_stored_user_can_be_recovered():
    comms_db = MockedCommunicationsBase()
    comms = CommunicationService(LocalCommunicationProvider(comms_db))

    user = User(
        localid="fakeid",
        number="+5499911234"
    )

    asyncio.run(comms.store_user(user))

    recovered_user = asyncio.run(comms.get_user("fakeid"))

    assert recovered_user == user


def test_sending_message_to_a_user():
    comms_db = MockedCommunicationsBase()
    comms_messager_log = MockedCommunicationsMessager()
    comms = CommunicationService(
        LocalCommunicationProvider(
            comms_db,
            comms_messager_log
        )
    )

    user = User(
        localid="fakeid",
        number="+54999111222"
    )

    asyncio.run(comms.store_user(user))
    message_text = "Congrats on being a new user"
    message = Message(user="fakeid",
                      message=message_text)

    asyncio.run(comms.send_message(message))

    last_sent = comms_messager_log.messages.pop()
    assert last_sent['message'] == message
    assert last_sent['to'] == user.number