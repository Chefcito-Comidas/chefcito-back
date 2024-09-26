from fastapi import status
from sqlalchemy import create_engine
from testcontainers.postgres import PostgresContainer
import pytest
from src.model.users.auth_request import AuthRequest
from src.model.users.permissions.base import DBEngine
from src.model.users.permissions.schema import AssociatedData, User, Base
from src.model.users.service import LocalUsersProvider
from src.model.users.update import UserUpdate
from test.services.db_load import run
from test.users.test_user_data import get_mocked_auth
from src.model.users.user_data import UserData

@pytest.mark.asyncio
async def test_postgres():
    with PostgresContainer('postgres:16') as postgres:
       Base.metadata.create_all(create_engine(postgres.get_connection_url()))
       run('db_config.yaml', connection=postgres.get_connection_url()) 
       database = DBEngine(conn_string=postgres.get_connection_url())
       firebase = get_mocked_auth()

       users_service = LocalUsersProvider(firebase, database, None) # type: ignore
       assert await users_service.is_allowed(AuthRequest(endpoint="/docs", id_token="anonymous")) == status.HTTP_200_OK
       database.insert_user(User(uid="User_1", email="user1@mail.com", user_type="client"),
                            AssociatedData(uid="User_1", name="User One", phone_number="123456789"))
       update = UserUpdate(
                name="jaimito suarez",
                phone="87654321"
                )
       await database.update_data("User_1", update)
       _, updated = database.get_user("User_1")
       assert updated.name == "jaimito suarez" #type: ignore
       assert updated.phone_number == "87654321" #type: ignore
        



