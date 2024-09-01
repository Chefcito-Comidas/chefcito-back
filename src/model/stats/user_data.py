from pydantic import BaseModel


class UserStatData(BaseModel):
    user: str
    total: int
    canceled: int
    expired: int