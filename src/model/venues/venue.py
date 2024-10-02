
from typing import Self
import datetime
from typing import List, Optional
from pydantic import BaseModel, field_validator
from src.model.commons.distance import LocalPosition
from src.model.venues.data.schema import VenueSchema
from src.model.venues.data.base import VenuesBase
import os
import json
from config import PROJECT_ROOT

json_path = os.path.join(PROJECT_ROOT, 'src', 'model', 'venues', 'data', 'characteristics.json')

with open(json_path) as f:
    FIXED_CHARACTERISTICS = json.load(f)["characteristics"]

json_path = os.path.join(PROJECT_ROOT, 'src', 'model', 'venues', 'data', 'features.json')

with open(json_path) as f:
    FIXED_FEATURES = json.load(f)["features"]


def validate_characteristics(characteristics: List[str]):
    for characteristic in characteristics:
        if characteristic not in FIXED_CHARACTERISTICS:
            raise ValueError(f"Invalid characteristic: {characteristic}")
    return characteristics

def validate_features(features: List[str]):
    for feature in features:
        if feature not in FIXED_FEATURES:
            raise ValueError(f"Invalid feature: {feature}")
    return features

def create_venue(name: str, location: str, capacity: int, logo: str, pictures: List[str], slots: List[datetime.datetime], characteristics: List[str], features: List[str],vacations: List[datetime.datetime], reservationLeadTime: int, menu: str) -> 'Venue':
    characteristics = validate_characteristics(characteristics)
    features = validate_features(features)
    return Venue(id="",
                 name=name, 
                 location=location, 
                 capacity=capacity,
                 logo=logo,
                 pictures=pictures,
                 slots=slots,
                 characteristics=characteristics, 
                 features=features,
                 vacations=vacations, 
                 reservationLeadTime=reservationLeadTime,
                 menu=menu,
                 status=Available())

class VenueStatus(BaseModel):

    status: str

    def get_status(self) -> str:
        return self.status

class Available(VenueStatus):

    def __init__(self):
        super().__init__(status="Available")

class Occupied(VenueStatus):

    def __init__(self):
        super().__init__(status="Occupied")

class Closed(VenueStatus):

    def __init__(self):
        super().__init__(status="Closed")

class Unconfirmed(VenueStatus):

    def __init__(self):
        super().__init__(status="Unconfirmed")


class CreateInfo(BaseModel):
    id: str
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
        return validate_characteristics(characteristics)
    
    @field_validator('features', mode='before')
    def validate_features(cls, features: List[str]):
        return validate_features(features)
    
    def into_venue(self) -> 'Venue':
        return Venue(id=self.id, 
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
                     menu=self.menu,
                     status=Available()) 


class Venue(BaseModel):

    id: str
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
    status: VenueStatus

    @field_validator('characteristics', mode='before')
    def validate_characteristics(cls, characteristics: List[str]):
        return validate_characteristics(characteristics)
    
    @field_validator('features', mode='before')
    def validate_features(cls, features: List[str]):
        return validate_features(features)
    
    def get_status(self) -> str:
        return self.status.get_status()

    def open(self):
        self.status = Available()

    def occupy(self):
        self.status = Occupied()

    def close(self):
        self.status = Closed()

    def unconfirm(self):
        self.status = Unconfirmed()

    def get_location(self) -> LocalPosition:
        lat_lon = self.location.split(",")
        try:
            return LocalPosition(self.id, lat_lon[0], lat_lon[1])
        except:
            return LocalPosition(self.id, "-34.594174", "-58.4566507")
    
    def persistance(self) -> VenueSchema:
        if not self.id:
            schema = VenueSchema.create(
                    self.name,
                    self.location,
                    self.capacity,
                    self.logo, 
                    self.pictures, 
                    self.slots,
                    self.characteristics, 
                    self.features,
                    self.vacations, 
                    self.reservationLeadTime,
                    self.menu,
                    self.status.get_status()
                    )
            self.id = schema.id.__str__()
            return schema
        else:
            return VenueSchema(
                    id=self.id,
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
                    menu=self.menu,
                    status=self.status.get_status()
                    )

    @staticmethod
    def delete(id: str, database: VenuesBase) -> None:
        return database.delete_venue(id)
    
    @classmethod
    def from_schema(cls, schema: VenueSchema) -> Self:
        return cls(id=schema.id.__str__(),
                   name=schema.name,
                   location=schema.location,
                   capacity=schema.capacity,
                   logo=schema.logo, 
                   pictures=schema.pictures, 
                   slots=schema.slots,
                   characteristics=schema.characteristics, 
                   features=schema.features,
                   vacations=schema.vacations, 
                   reservationLeadTime=schema.reservationLeadTime,
                   menu=schema.menu,
                   status=VenueStatus(status=schema.status)
                   )
