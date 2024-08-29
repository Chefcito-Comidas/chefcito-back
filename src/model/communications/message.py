from pydantic import BaseModel


class Message(BaseModel):
    user: str
    message: str 