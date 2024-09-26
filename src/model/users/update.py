
from typing import Optional

from pydantic import BaseModel


class UserUpdate(BaseModel):
    name: Optional[str]
    phone: Optional[str]

