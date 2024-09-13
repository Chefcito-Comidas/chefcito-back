import datetime
from typing import List, Optional
from pydantic import BaseModel, field_validator
from src.model.venues.venue import Venue
import os
import json
from config import PROJECT_ROOT

json_path = os.path.join(PROJECT_ROOT, 'src', 'model', 'venues', 'data', 'characteristics.json')

with open(json_path) as f:
    FIXED_CHARACTERISTICS = json.load(f)["characteristics"]

class Update(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    capacity: Optional[int] = None
    logo: Optional[str] = None
    pictures: Optional[List[str]] = None
    slots: Optional[List[datetime.datetime]] = None
    characteristics: Optional[List[str]] = None
    vacations: Optional[List[datetime.datetime]] = None
    reservationLeadTime: Optional[int] = None
    menu: Optional[str] = None
    open: Optional[bool] = False
    close: Optional[bool] = False
    occupy: Optional[bool] = False  


    @field_validator('characteristics', mode='before')
    def validate_characteristics(cls, characteristics: Optional[List[str]]):
        if characteristics:
            for characteristic in characteristics:
                if characteristic not in FIXED_CHARACTERISTICS:
                    raise ValueError(f"Invalid characteristic: {characteristic}")
        return characteristics
    
    def modify(self, venue: Venue) -> Venue:

        if self.close:
            venue.close()
            return venue

        if self.open:
            venue.open()
            return venue

        if self.occupy:
            venue.occupy()
            return venue

        if self.name:
            venue.name = self.name
            venue.unconfirm()

        if self.location:
            venue.location = self.location
            venue.unconfirm()

        if self.capacity:
            venue.capacity = self.capacity
            venue.unconfirm()

        if self.logo:
            venue.logo = self.logo
            venue.unconfirm()
        
        if self.pictures:
            venue.pictures = self.pictures
            venue.unconfirm()

        if self.slots:
            venue.slots = self.slots
            venue.unconfirm()

        if self.characteristics:
            venue.characteristics = self.characteristics
            venue.unconfirm()

        if self.vacations:
            venue.vacations = self.vacations
            venue.unconfirm()
        
        if self.reservationLeadTime:
            venue.reservationLeadTime = self.reservationLeadTime
            venue.unconfirm()

        if self.menu:
            venue.menu = self.menu
            venue.unconfirm()
        return venue
