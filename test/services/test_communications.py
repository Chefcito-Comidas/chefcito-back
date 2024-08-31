import pytest
from sqlalchemy import create_engine
from testcontainers.postgres import PostgresContainer

from src.model.communications.data.base import CommunicationsBase, RelCommunicationsBase
from src.model.communications.data.user_schema import CommsSchema
from src.model.communications.service import LocalCommunicationProvider
from src.model.communications.user import User


def prepare_postgres_base(at: str):
    local_engine = create_engine(at)
    CommsSchema.metadata.create_all(local_engine) 

@pytest.mark.asyncio
async def test_user_number_base():
    with PostgresContainer('postgres:16') as postgres:
        prepare_postgres_base(postgres.get_connection_url())
        database = RelCommunicationsBase(postgres.get_connection_url())
        provider = LocalCommunicationProvider(database)
        user = User(
            localid="fakeid",
            number="+54111222333"
        )
        await provider.store_user(user)
        result = await provider.get_user("fakeid")
        assert result == user