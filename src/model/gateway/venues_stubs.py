import datetime
from typing import List
from pydantic import BaseModel, field_validator
import src.model.venues.venue as venues
import os
import json
from config import PROJECT_ROOT

json_path = os.path.join(PROJECT_ROOT, 'src', 'model', 'venues', 'data', 'characteristics.json')

with open(json_path) as f:
    FIXED_CHARACTERISTICS = json.load(f)["characteristics"]

class CreateInfo(BaseModel):
    name: str
    location: str
    capacity: int
    logo: str
    pictures: List[str]
    slots: List[datetime.datetime]
    characteristics: List[str]
    vacations: List[datetime.datetime]
    reservationLeadTime: int
    menu: str

    @field_validator('characteristics', mode='before')
    def validate_characteristics(cls, characteristics: List[str]):
        if not isinstance(characteristics, list):
            raise ValueError("Characteristics must be a list")
        for characteristic in characteristics:
            if characteristic not in FIXED_CHARACTERISTICS:
                raise ValueError(f"Invalid characteristic: {characteristic}")
        return characteristics

    def into_create_info(self, id: str) -> venues.CreateInfo:
        return venues.CreateInfo(
            id=id,
            name=self.name,
            location=self.location,
            capacity=self.capacity,
            logo=self.logo,
            pictures=self.pictures,
            slots=self.slots,
            characteristics=self.characteristics,
            vacations=self.vacations,
            reservationLeadTime=self.reservationLeadTime,
            menu=self.menu
        )
