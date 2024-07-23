from pydantic import BaseModel
from typing import Self

class Error(BaseModel):
    description: str = "An error occured"
    endpoint: str = "/api/call"
    
    @classmethod
    def from_exception(cls, exception: Exception, endpoint: str = "/api/call") -> Self:
        return cls(endpoint=endpoint, description=f"{exception}")
