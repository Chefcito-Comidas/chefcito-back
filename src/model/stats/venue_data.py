from pydantic import BaseModel


class VenueStatData(BaseModel):
    venue: str
    total: int
    canceled: float
    expired: float

    def __increase(self, canceled: float, expired: float):
        canceled += self.canceled * self.total
        expired += self.expired * self.total
        self.total += 1
        self.canceled = canceled / self.total
        self.expired = expired / self.total

    def increase(self):
        self.__increase(0, 0)

    def increase_canceled(self):
        self.__increase(1, 0)

    def increase_expired(self):
        self.__increase(0, 1)

