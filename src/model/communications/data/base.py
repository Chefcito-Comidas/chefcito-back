from typing import Callable
from sqlalchemy import create_engine, select
from src.model.commons.session import with_no_commit, with_session
from src.model.communications.data.user_schema import UserSchema
from src.model.communications.user import User
from sqlalchemy.orm import Session


DEFAULT_POOL_SIZE = 5

class CommunicationsBase():

    async def store_user(self, user: User) -> None:
        raise Exception("Interface method should not be called")

    async def get_user(self, user_id: str) -> User | None:
        raise Exception("Interface method should not be called")

    async def update_user(self, user: User) -> None:
        raise Exception("Interface method should not be called")

class RelCommunicationsBase(CommunicationsBase):

    def __init__(self, conn_string: str, **kwargs):
        kwargs["pool_size"] = kwargs.get("pool_size", DEFAULT_POOL_SIZE)
        kwargs["pool_recyle"] = 30
        self.__engine = create_engine(conn_string, pool_pre_ping=True, **kwargs)

    def __store_call(self, user: User) -> Callable[[Session], None]:
        def call(session: Session):
            schema = user.into_schema()
            session.add(schema)
        return call

    def __get_call(self, id: str) -> Callable[[Session], User | None]:
        def call(session: Session) -> User | None:
            query = select(UserSchema).where(UserSchema.id.__eq__(id))
            result = session.execute(query).scalar()
            return User.from_schema(result)

        return call

    def __update_call(self, user: User) -> Callable[[Session], None]:
        def call(session: Session) -> None:
            query = select(UserSchema).where(UserSchema.id.__eq__(user.localid))
            recovered = session.execute(query).scalar()
            if recovered:
                recovered.number = user.number
        return call

    async def store_user(self, user: User) -> None:
        call = self.__store_call(user)
        with_session(call)(self.__engine)

    async def get_user(self, user_id: str) -> User | None:
        call = self.__get_call(user_id)
        return with_no_commit(call)(self.__engine)

    async def update_user(self, user: User) -> None:
        call = self.__update_call(user)
        with_session(call)(self.__engine)

class MockedCommunicationsBase(CommunicationsBase):

    def __init__(self):
        self.base = {}

    async def store_user(self, user: User) -> None:
        self.base[user.localid] = user

    async def get_user(self, user_id: str) -> User | None:
        return self.base.get(user_id, None)
