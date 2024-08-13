from typing import Self
from pydantic import BaseModel

from src.model.communications.data.user_schema import UserSchema


class User(BaseModel):
    localid: str
    number: str

    def into_schema(self) -> UserSchema:
        return UserSchema(
            id=self.localid,
            number=self.number
        ) 
    
    @classmethod
    def from_schema(cls, schema: UserSchema | None) -> Self | None:
        if not schema:
            return None
        return cls(localid=schema.id, number=schema.number)