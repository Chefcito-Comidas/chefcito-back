from fastapi import status
from testcontainers.postgres import PostgresContainer
import pytest
from src.model.users.auth_request import AuthRequest
from src.model.users.permissions.base import DBEngine
from src.model.users.service import LocalUsersProvider
from test.services.db_load import run
from test.users.test_user_data import get_mocked_auth

@pytest.mark.asyncio
async def test_postgres():
    with PostgresContainer('postgres:16') as postgres:
       run('db_config.yaml', connection=postgres.get_connection_url()) 
       database = DBEngine(conn_string=postgres.get_connection_url())
       firebase = get_mocked_auth()
       users_service = LocalUsersProvider(firebase, database)
       assert await users_service.is_allowed(AuthRequest(endpoint="/docs", id_token="anonymous")) == status.HTTP_200_OK





