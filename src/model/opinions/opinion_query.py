from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class OpinionQuery(BaseModel):

    venue: Optional[str] = None
    from_date: Optional[datetime] = None  
    to_date: Optional[datetime] = None
