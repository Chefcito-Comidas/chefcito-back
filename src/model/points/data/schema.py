from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.model.points.point import Point

class PointsBaseSchema(DeclarativeBase):
    pass

class PointSchema(PointsBaseSchema):

    __tablename__ = "points"

    total: Mapped[int] = mapped_column()
    user: Mapped[str] = mapped_column(primary_key=True)

    @classmethod
    def from_points(cls, points: Point) -> 'PointSchema':
        return cls(total=points.total, user=points.user)