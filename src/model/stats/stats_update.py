from pydantic import BaseModel

from src.model.stats.data.base import StatsDB
from src.model.stats.data.user_data import UserDataDocument


class DataUpdate:

    async def update(self, db: StatsDB):
        raise Exception("Tried to do an invalid update")


class UserCancelUpdate(BaseModel, DataUpdate):
    user: str

    async def update(self, db: StatsDB):
        user = await db.get_by_user(self.user)
        user.canceled += 1
        await db.update_user_data(user) 


class StatsUpdate():

    def __init__(self, user: str):
        self.user = user
        self.update_data: DataUpdate = DataUpdate() 


    def canceled_reservation(self):
        self.update_data = UserCancelUpdate(user=self.user)

    async def update(self, db: StatsDB):
        await self.update_data.update(db)