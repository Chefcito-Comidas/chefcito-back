from datetime import datetime, timedelta, timezone
from pydantic import BaseModel


class Summary(BaseModel):

    text: str
    date: datetime
    venue: str

    def __get_last_possible_date(self) -> datetime:
        return (datetime.today() - timedelta(days=15)).replace(tzinfo=timezone.utc)

    def is_too_old(self) -> bool:
        return self.date < self.__get_last_possible_date()
