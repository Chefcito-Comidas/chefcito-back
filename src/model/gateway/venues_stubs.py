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

json_path = os.path.join(PROJECT_ROOT, 'src', 'model', 'venues', 'data', 'features.json')

with open(json_path) as f:
    FIXED_FEATURES = json.load(f)["features"]

class CreateInfo(BaseModel):
    name: str
    location: str
    capacity: int
    logo: str
    pictures: List[str]
    slots: List[datetime.datetime]
    characteristics: List[str]
    features: List[str]
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

    @field_validator('features', mode='before')
    def validate_features(cls, features: List[str]):
        if not isinstance(features, list):
            raise ValueError("Features must be a list")
        for feature in features:
            if feature not in FIXED_FEATURES:
                raise ValueError(f"Invalid feature: {feature}")
        return features
    
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
            features=self.features,
            vacations=self.vacations,
            reservationLeadTime=self.reservationLeadTime,
            menu=self.menu
        )
