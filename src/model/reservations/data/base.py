from collections.abc import Callable
from typing import List
from uuid import UUID
from sqlalchemy.orm import Session
from src.model.commons.session import with_no_commit, with_session
from src.model.reservations.data.schema import ReservationSchema
from sqlalchemy import Select, create_engine, delete, select, update

# TODO: try to add this to configuration options
DEFAULT_POOL_SIZE = 5

class ReservationsBase:

    def get_by_eq(self, query: Select) -> List[ReservationSchema]:
        raise Exception("Interface method should not be used")

    def store_reservation(self, reservation: ReservationSchema) -> None:
        """
            Stores a reservation on the base,
            if the reservation is already stored then
            fails
        """
        raise Exception("Interface method should not be called")

    def run_count(self, query: Select) -> int:
        """
            Runs a query that returns the total number of rows
            based on certain restrictions (given in the Select query)
        """
        raise Exception("Interface method should not be called")

    def update_reservation(self, reservation: ReservationSchema) -> None:
        """
            Updates information about a reservation
        """
        raise Exception("Interface method should not be called")

    def get_reservation_by_id(self, id: str) -> ReservationSchema | None:
        """
            Searches for a reservation based on the id
            given
        """
        raise Exception("Interface method should not be called")

    def delete_reservation(self, id: str) -> None:
        """
            Deletes a reservation
        """
        raise Exception("Interface method should not be called")

class RelBase(ReservationsBase):

    def __init__(self, conn_string: str, **kwargs):
        kwargs["pool_size"] = kwargs.get("pool_size", DEFAULT_POOL_SIZE)
        kwargs["pool_recyle"] = 30
        self.__engine = create_engine(conn_string)

    def __get_by_eq(self, query: Select) -> Callable[[Session], List[ReservationSchema]]:
        def call(session: Session):
            result = list(session.execute(query).scalars())
            return result
        return call

    def run_count(self, query: Select) -> int:
        call = with_no_commit(lambda s: s.execute(query).scalar())
        return call(self.__engine)

    def get_by_eq(self, query: Select) -> List[ReservationSchema]:
        call = with_no_commit(self.__get_by_eq(query))
        return call(self.__engine)

    def __store_reservation(self, reservation: ReservationSchema) -> Callable[[Session], None]:
        def call(session: Session) -> None:
            session.add(reservation)

        return call

    def store_reservation(self, reservation: ReservationSchema) -> None:
        call = with_session(self.__store_reservation(reservation))
        return call(self.__engine)

    def __update_reservation(self, reservation: ReservationSchema) -> Callable[[Session], None]:
        def call(session: Session) -> None:
            value = session.get(ReservationSchema, reservation.id)
            if not value:
                return
            value.status = reservation.status
            value.time = reservation.time
            value.people = reservation.people
        return call

    def update_reservation(self, reservation: ReservationSchema) -> None:
        call = with_session(self.__update_reservation(reservation))
        return call(self.__engine)

    def __get_reservation_by_id(self, id: str) -> Callable[[Session], ReservationSchema | None]:
        def call(session: Session) -> ReservationSchema | None:
            query = select(ReservationSchema).where(ReservationSchema.id.__eq__(id))
            result = session.scalar(query)
            return result
        return call

    def get_reservation_by_id(self, id: str) -> ReservationSchema | None:
        call = with_no_commit(self.__get_reservation_by_id(id))

        return call(self.__engine)

    def __delete_reservation(self, id: str) -> Callable[[Session], None]:
        def call(session: Session) -> None:
            query = delete(ReservationSchema).where(ReservationSchema.id.__eq__(id))
            session.execute(query)

        return call


    def delete_reservation(self, id: str) -> None:
        call = with_session(self.__delete_reservation(id))
        call(self.__engine)

class MockBase(ReservationsBase):

    def __init__(self):
        self.base: List[ReservationSchema] = []

    def store_reservation(self, reservation: ReservationSchema) -> None:
        for stored in self.base:
            if stored.id == reservation.id:
                raise Exception("Reservation already exists")
        self.base.append(reservation)


    def update_reservation(self, reservation: ReservationSchema) -> None:
        for index, stored in enumerate(self.base):
            if stored.id == reservation.id:
                self.base[index] = reservation
                return

    def get_reservation_by_id(self, id: str) -> ReservationSchema | None:

        for stored in self.base:
            if stored.id == id:
                return stored

    def delete_reservation(self, id: str) -> None:
        for index, stored in enumerate(self.base):
            if stored.id == id:
                self.base.pop(index)
                return
        return
