
from typing import Annotated, Self
from beanie import Document, Indexed

from src.model.stats.user_data import UserStatData



class UserDataDocument(Document):
    user: Annotated[str, Indexed()]
    total: int
    canceled: int
    expired: int

    def into_stat_data(self) -> UserStatData:
        if self.total == 0:
            return UserStatData(user=self.user, total=0, canceled=0, expired=0)
        return UserStatData(
            user=self.user,
            total=self.total,
            canceled=round(self.canceled/self.total, 2),
            expired=round(self.expired/self.total, 2)
        )
    
    def update_from(self, stat: UserStatData):
        self.total = stat.total
        self.canceled = round(stat.total * stat.canceled)
        self.expired = round(stat.expired * stat.total)