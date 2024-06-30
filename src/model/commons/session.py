from collections.abc import Callable
from typing import Any
from sqlalchemy.orm import Session
from sqlalchemy import Engine

def with_session(call: Callable[[Session], Any]) -> Callable[[Engine], Any]:
    """
        Returns a wrapper over the function passed
        as an argument that takes care of creating, commiting
        and closing the session
    """
    def callee(engine: Engine) -> Any:
        session = Session(engine)
        result = call(session)
        session.commit()
        session.close()
        return result

    return callee

def with_no_commit(call: Callable[[Session], Any]) -> Callable[[Engine], Any]:
    """
        Same as with_session, but does not call commit.
        Works for queries that require to select a value/values
        but that do not change the underlying data
    """
    def callee(engine: Engine) -> Any:
        session = Session(engine)
        result = call(session)
        session.close()
        return result

    return callee
