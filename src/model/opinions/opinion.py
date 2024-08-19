from datetime import datetime
from pydantic import BaseModel


class Opinion(BaseModel):

    venue: str
    opinion: str
    reservation: str
    date: datetime
