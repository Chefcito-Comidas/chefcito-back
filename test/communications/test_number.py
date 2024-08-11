import asyncio
import pytest

from src.model.communications.data.base import MockedCommunicationsBase
from src.model.communications.service import CommunicationService, LocalCommunicationProvider
from src.model.communications.user import User

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
