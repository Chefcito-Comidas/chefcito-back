from datetime import datetime
from pydantic import BaseModel


class Summary(BaseModel):

    text: str
    date: datetime
    venue: str
