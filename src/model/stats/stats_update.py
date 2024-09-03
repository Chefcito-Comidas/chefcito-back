from pydantic import BaseModel

from src.model.reservations.reservation import Assisted, Canceled, Expired, Reservation
from src.model.stats.data.base import StatsDB
from src.model.stats.data.user_data import UserDataDocument


class DataUpdate:

    async def update(self, db: StatsDB):
        raise Exception("Tried to do an invalid update")


class UserCancelUpdate(BaseModel, DataUpdate):
    user: str
    venue: str

    async def update(self, db: StatsDB):
        user = await db.get_by_user(self.user)
        venue = await db.get_by_venue(self.venue)
        user.increase_canceled()
        venue.increase_canceled() 
        await db.update_user_data(user)
        await db.update_venue_data(venue) 

class UserExpiredUpdate(BaseModel, DataUpdate):
    user: str
    venue: str

    async def update(self, db: StatsDB):
        user = await db.get_by_user(self.user)
        venue = await db.get_by_venue(self.venue)
        user.increase_expired()
        venue.increase_expired() 
        await db.update_user_data(user)
        await db.update_venue_data(venue)

class UserTotalUpdate(BaseModel, DataUpdate):
    user: str
    venue: str
    people: int

    async def update(self, db: StatsDB):
        user = await db.get_by_user(self.user)
        venue = await db.get_by_venue(self.venue)
        user.increase()
        venue.increase() 
        venue.update_people(self.people)
        await db.update_user_data(user)
        await db.update_venue_data(venue)

   

class StatsUpdate():

    def __init__(self, user: str, venue: str):
        self.user = user
        self.venue = venue
        self.update_data: DataUpdate = DataUpdate() 
        self.people = 0


    @classmethod
    def from_reservation(cls, reservation: Reservation) -> 'StatsUpdate':
        update = cls(user=reservation.user, venue=reservation.venue)
        if reservation.get_status() == Expired().get_status():
            update.expired_reservation()
        elif reservation.get_status() == Assisted().get_status():
            update.people = reservation.people
            update.assisted_reservation()
        elif reservation.get_status() == Canceled().get_status():
            update.canceled_reservation()
        return update

    def canceled_reservation(self):
        self.update_data = UserCancelUpdate(user=self.user, venue=self.venue)

    def expired_reservation(self):
        self.update_data = UserExpiredUpdate(user=self.user, venue=self.venue)

    def assisted_reservation(self):
        self.update_data = UserTotalUpdate(user=self.user, venue=self.venue, people=self.people)

    async def update(self, db: StatsDB):
        await self.update_data.update(db)