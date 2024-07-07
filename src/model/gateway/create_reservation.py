
from pydantic import BaseModel
import src.model.reservations.reservation as r 

class CreateInfo(BaseModel):
    venue: str
    time: str
    people: int

    def with_user(self, user: str) -> r.CreateInfo:
        info = r.CreateInfo(user="",venue=self.venue, time=self.time, people=self.people)
        info.change_user(user)
        return info


