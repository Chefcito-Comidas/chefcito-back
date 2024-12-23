from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.model.points.point import Point

class PointsBaseSchema(DeclarativeBase):
    pass

class PointSchema(PointsBaseSchema):

    __tablename__ = "points"

    total: Mapped[int] = mapped_column()
    user: Mapped[str] = mapped_column(primary_key=True)
    last_updated: Mapped[datetime] = mapped_column()    
    
    def into_points(self) -> Point:
        return Point(total=self.total, user=self.user)

    @classmethod
    def from_points(cls, points: Point, time: datetime = datetime.now()) -> 'PointSchema':
        return cls(total=points.total, user=points.user, last_updated=time)
