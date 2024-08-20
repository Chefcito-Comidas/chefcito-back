import uuid
from typing import List
import sqlalchemy
from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy.orm import Mapped
from typing import Self
from sqlalchemy import String, DateTime
from sqlalchemy.dialects.postgresql import ARRAY
import datetime
from typing import List


class VenuesBase(DeclarativeBase):
    pass


class VenueSchema(VenuesBase):
    __tablename__ = "venues"

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column()
    location: Mapped[str] = mapped_column()
    capacity: Mapped[int] = mapped_column()
    logo: Mapped[str] = mapped_column()
    pictures: Mapped[List[str]] = mapped_column(ARRAY(String))
    slots: Mapped[List[datetime.datetime]] = mapped_column(ARRAY(DateTime))
    characteristics: Mapped[List[str]] = mapped_column(ARRAY(String))
    vacations: Mapped[List[datetime.datetime]] = mapped_column(ARRAY(DateTime))
    reservationLeadTime: Mapped[int] = mapped_column()
    status: Mapped[str] = mapped_column()



    def __repr__(self) -> str:
        return (f"Venue(id={self.id}, name={self.name}, location={self.location}, "
                f"capacity={self.capacity}, "
                f"logo={self.logo}, pictures={self.pictures}, slots={self.slots}), "
                f"characteristics={self.characteristics}), vacations={self.vacations}), "
                f"reservationLeadTime={self.reservationLeadTime}), status={self.status}")
    
    @classmethod
    def create(cls, name: str, location: str, capacity: int, logo: str, pictures: List[str], slots: List[datetime.datetime], characteristics: List[str], vacations: List[datetime.datetime], reservationLeadTime: int, status: str) -> Self:
        uid = uuid.uuid1()
        uid_string=uid.__str__()
        return cls(id=uid_string, name=name, location=location, capacity=capacity, status=status, logo=logo, pictures=pictures, slots=slots, characteristics=characteristics, vacations=vacations, reservationLeadTime=reservationLeadTime )
