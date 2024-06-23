import uuid
import sqlalchemy
from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy.orm import Mapped
from typing import Self

class ReservationsBase(DeclarativeBase):
    pass

class ReservationSchema(ReservationsBase):
    __tablename__ = "reservations"

    id: Mapped[str] = mapped_column(primary_key=True)
    user: Mapped[str] = mapped_column()
    venue: Mapped[str] = mapped_column()
    time: Mapped[str] = mapped_column()
    people: Mapped[int] = mapped_column()
    status: Mapped[str] = mapped_column()

    def __repr__(self) -> str:
        return f"{self.id}:{self.user}:{self.venue}/at:{self.time}/for:{self.people}/{self.status}"
    
    @classmethod
    def create(cls, user: str, venue: str, time: str, people: int, status: str) -> Self:
        uid = uuid.uuid1()
        return cls(id=uid.__str__(), user=user, venue=venue, time=time, people=people, status=status)

