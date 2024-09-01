
from typing import Annotated, Self
from beanie import Document, Indexed



class UserDataDocument(Document):
    user: Annotated[str, Indexed()]
    total: int
    canceled: int
    expired: int

   