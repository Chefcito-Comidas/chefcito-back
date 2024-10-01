from copy import copy
from random import shuffle
from src.model.commons.distance import DistanceRanker, LocalPosition, RelativeDistance


def test_distance_between_anchorage_and_centenario():
   anchorage = LocalPosition("anchorage", "61.2035833", "-149.853936")
   centenario = LocalPosition("centenario", "-34.6071389", "-58.4383249")

   expected_distance = 13398.755726725843
   result = anchorage.distance_to(centenario)

   assert abs(expected_distance - result) < 0.1

def test_compare_distances_relative_to_a_point():
    my_position = LocalPosition("my_position", "-34.6211119", "-58.4348481")
    anchorage = LocalPosition("anchorage", "61.2035833", "-149.853936")
    centenario = LocalPosition("centenario", "-34.6071389", "-58.4383249")
    
    to_anchorage = RelativeDistance(my_position, anchorage)
    to_centenario = RelativeDistance(my_position, centenario)

    assert to_anchorage > to_centenario
    assert to_anchorage != to_centenario
    assert to_centenario < to_anchorage
    assert to_centenario <= to_anchorage
    assert to_anchorage >= to_centenario


def test_two_nearly_equal_distances_should_be_equal():
    my_position = LocalPosition("my_position", "-34.6211119", "-58.4348481")
    centenario = LocalPosition("centenario", "-34.6071389", "-58.4383249")
    centenario_2 = LocalPosition("centenario_2", "-34.6071388", "-58.4383249")

    to_centenario_1 = RelativeDistance(my_position, centenario)
    to_centenario_2 = RelativeDistance(my_position, centenario_2)

    assert  to_centenario_1 == to_centenario_2
    assert  to_centenario_1 <= to_centenario_2
    assert to_centenario_1 >= to_centenario_2

def test_ranking_distances_without_filtering():
    my_position = LocalPosition("my_position", "-34.6071389", "-58.4383249")
    base = (-34.6071389, -58.4383249)
    positions = []
    for i in range(0, 200):
        positions.append((base[0] + 0.01 * i, base[1] + 0.01 * i))
    places = []
    for position in positions:
        places.append(
            LocalPosition(f"{position[0]},{position[1]}", position[0].__str__(), position[1].__str__())
        )
    ranker = DistanceRanker(my_position)
    places_copied = copy(places)
    shuffle(places)
    i = 0
    while i < len(places):
        batch = places[i:i+10]
        ranker.add_batch(batch)
        i += 10
    final_result = ranker.sort()
    print(len(final_result))
    for i in range(0,200):
        assert final_result[i][0] == places_copied[i] 
    
