import uuid
from chefcito_cli.scripts.db_load import mapped_column
import sqlalchemy
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from typing import Self

class VenuesBase(DeclarativeBase):
    pass


class VenueSchema(VenuesBase):
    __tablename__ = "venues"

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    location: Mapped[str] = mapped_column()
    capacity: Mapped[int] = mapped_column()
    status: Mapped[str] = mapped_column()

    def __repr__(self) -> str:
        return f"{self.id}:{self.name}/{self.location}/capacity:{self.capacity}/{self.status}"

    @classmethod
    def create(cls, name: str, location: str, capacity: int, status: str) -> Self:
        uid = uuid.uuid1()
        uid_string=uid.__str__()
        return cls(id=uid_string, name=name, location=location, capacity=capacity, status=status)
