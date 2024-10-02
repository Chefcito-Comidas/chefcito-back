from typing import Self
import uuid
from typing import List
import sqlalchemy
from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy.orm import Mapped
from sqlalchemy import String, DateTime
from sqlalchemy.dialects.postgresql import ARRAY
import datetime
import os
import json
from config import PROJECT_ROOT

json_path = os.path.join(PROJECT_ROOT, 'src', 'model', 'venues', 'data', 'characteristics.json')

with open(json_path) as f:
    FIXED_CHARACTERISTICS = json.load(f)["characteristics"]

def validate_characteristics(characteristics: List[str]) -> None:
    for characteristic in characteristics:
        if characteristic not in FIXED_CHARACTERISTICS:
            raise ValueError(f"Invalid characteristic: {characteristic}")
        

json_path = os.path.join(PROJECT_ROOT, 'src', 'model', 'venues', 'data', 'features.json')

with open(json_path) as f:
    FIXED_FEATURES = json.load(f)["features"]


def validate_features(features: List[str]):
    for feature in features:
        if feature not in FIXED_FEATURES:
            raise ValueError(f"Invalid feature: {feature}")
    return features
        
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
    features: Mapped[List[str]] = mapped_column(ARRAY(String))
    vacations: Mapped[List[datetime.datetime]] = mapped_column(ARRAY(DateTime))
    reservationLeadTime: Mapped[int] = mapped_column()
    menu: Mapped[str] = mapped_column()
    status: Mapped[str] = mapped_column()



    def __repr__(self) -> str:
        return (f"Venue(id={self.id}, name={self.name}, location={self.location}, "
                f"capacity={self.capacity}, "
                f"logo={self.logo}, pictures={self.pictures}, slots={self.slots}), "
                f"characteristics={self.characteristics}), features={self.features}),vacations={self.vacations}), "
                f"reservationLeadTime={self.reservationLeadTime}), menu={self.menu},status={self.status}")
    
    @classmethod
    def create(cls, name: str, location: str, capacity: int, logo: str, pictures: List[str], slots: List[datetime.datetime], characteristics: List[str], features: List[str], vacations: List[datetime.datetime], reservationLeadTime: int, menu: str, status: str) -> Self:
        validate_characteristics(characteristics)
        validate_features(features)
        uid = uuid.uuid1()
        uid_string=uid.__str__()
        return cls(id=uid_string, name=name, location=location, capacity=capacity, status=status, logo=logo, pictures=pictures, slots=slots, characteristics=characteristics, features=features, vacations=vacations, reservationLeadTime=reservationLeadTime, menu=menu )
