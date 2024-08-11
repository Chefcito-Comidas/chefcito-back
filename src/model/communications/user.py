from pydantic import BaseModel


class User(BaseModel):
    localid: str
    number: str

