from src.model.communications.user import User


class CommunicationsBase():

    async def store_user(self, user: User) -> None:
        raise Exception("Interface method should not be called")
    
    async def get_user(self, user_id: str) -> User | None:
        raise Exception("Interface method should not be called")


class MockedCommunicationsBase(CommunicationsBase):
    
    def __init__(self):
        self.base = {}

    async def store_user(self, user: User) -> None:
        self.base[user.localid] = user

    async def get_user(self, user_id: str) -> User | None:
        return self.base.get(user_id, None)