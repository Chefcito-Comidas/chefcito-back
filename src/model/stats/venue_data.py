from pydantic import BaseModel

from src.model.reservations.reservation import Expired


class VenueStatData(BaseModel):
    venue: str
    total: int
    canceled: float
    expired: float
    people: float 

    def __increase(self, canceled: float, expired: float):
        canceled += self.canceled * self.total
        expired += self.expired * self.total
        self.total += 1
        self.canceled = canceled / self.total
        self.expired = expired / self.total

    def __accepted(self) -> float:
        return self.total * (1 - self.canceled - self.expired)

    def update_people(self, people: float):
        people += self.people * self.__accepted()
        self.people = people / self.total 

    def increase(self):
        self.__increase(0, 0)

    def increase_canceled(self):
        self.__increase(1, 0)

    def increase_expired(self):
        self.__increase(0, 1)

