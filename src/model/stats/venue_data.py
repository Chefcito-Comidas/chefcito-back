import datetime
from typing import Dict, List, Tuple
from pydantic import BaseModel

from src.model.reservations.reservation import Expired


class VenueMeanPerDay(BaseModel):
    """
        I store days based on datetime.weekday
        monday is 0 and sunday is 6.
        On each day I have a Tuple with the reservations
        made for that particular day that were succesful
    """
    means: Dict[int, int] = {}

    def get_day(self, day: int) -> int:
        return self.means.get(day, 0)

    def update(self, day: datetime.datetime):
        val = self.get_day(day.weekday())
        self.means[day.weekday()] = val + 1

class VenueMeanPerTurn(BaseModel):
    turns: Dict[str, int] = {}

    def get_turns(self) -> List[Tuple[str, int]]:
        return list(self.turns.items())

    def update(self, day: datetime.datetime):
        turn = f"{day.hour:02d}:{day.minute:02d}"
        val = self.turns.get(turn, 0)
        self.turns[turn] = val + 1

class VenueStatData(BaseModel):
    venue: str
    total: int
    canceled: float
    expired: float
    people: float
    days: VenueMeanPerDay = VenueMeanPerDay()
    turns: VenueMeanPerTurn = VenueMeanPerTurn()


    def __increase(self, canceled: float, expired: float):
        canceled += self.canceled * self.total
        expired += self.expired * self.total
        self.total += 1
        self.canceled = canceled / self.total
        self.expired = expired / self.total

    def __accepted(self) -> float:
        return (self.total-1) * (1 - self.canceled - self.expired)

    def __update_people(self, people: float):
        people += self.people * self.__accepted()
        self.people = people / (self.total * (1 - self.canceled - self.expired))

    def increase(self, people: int, day: datetime.datetime):
        self.__increase(0, 0)
        self.__update_people(people)
        self.days.update(day)
        self.turns.update(day)

    def increase_canceled(self):
        self.__increase(1, 0)

    def increase_expired(self):
        self.__increase(0, 1)

    def get_turns(self) -> List[Tuple[str, float]]:
        turns = self.turns.get_turns()
        #I need to divide turns by the total value
        return list(
            map(
            lambda x: (x[0], x[1]/self.total),
            turns
            )
        )

    def get_day(self, day: int) -> float:
        return self.days.get_day(day) / self.total
