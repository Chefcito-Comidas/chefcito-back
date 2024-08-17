from typing import List, Self
import haversine as hs

class LocalPosition:

    def __init__(self, id: str, lat: str, lon: str):
        self.id = id
        try:
            lat_float = float(lat)
        except:
            raise Exception(f"Invalid latitude: {lat}")
        try:
            lon_float = float(lon)
        except:
            raise Exception(f"Ivalid longitude: {lon}")

        self.location = (lat_float, lon_float)

    def distance_to(self, other: Self) -> float:
        return hs.haversine(self.location, other.location)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, LocalPosition) and \
        self.id == other.id and self.location == other.location

class RelativeDistance:

    def __init__(self, point: LocalPosition, to: LocalPosition):
        self.point = point
        self.to = to
        self.distance = point.distance_to(to)

    def __eq__(self, value: object) -> bool:
        """
            Returns if to distances are equal:
            two places are considered equally away if their
            distances relative to the position do not difere
            more than 10 meter (0.01 km)
        """
        return isinstance(value, RelativeDistance) and \
                abs(self.distance - value.distance) <= 0.01
    
    def __ne__(self, value: object) -> bool:
        return not (self == value)
    
    def __lt__(self, value: object) -> bool:
        return isinstance(value, RelativeDistance) and \
                self.distance - value.distance < -0.01
    
    def __le__(self, value: object) -> bool:
        return self == value or self < value

    def __gt__(self, value: object) -> bool:
        return not (self <= value)
    
    def __ge__(self, value: object) -> bool:
        return self == value or self > value

    

class DistanceRanker:

    def __init__(self, point: LocalPosition):
        self.rank: List[List[RelativeDistance]] = []
        self.point = point

    def add_batch(self, batch: List[LocalPosition]) -> None:
        processed = list(
            map(
                lambda point: RelativeDistance(self.point, point),
                batch
            )
        ) 
        processed.sort()
        self.rank.append(processed)

    def __merge_two(self) -> None:
        right = self.rank.pop()
        left = self.rank.pop()
        result = []
        while right and left:
            if right[0] < left[0]:
                result.append(right.pop(0))
            else:
                result.append(left.pop(0))
        while right:
            result.append(right.pop(0))
        while left:
            result.append(left.pop(0))
        self.rank.append(result)

    def sort(self) -> List[LocalPosition]:
        while len(self.rank) > 1:
            self.__merge_two()
        return list(
            map(
            lambda value: value.to,
            self.rank[0]
            )
        )