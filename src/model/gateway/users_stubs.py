from pydantic import BaseModel
from src.model.points.point import Point, PointResponse
import src.model.users.user_data as ud

class UserData(BaseModel):
   data: ud.UserData
   points: PointResponse 
