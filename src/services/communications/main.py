from typing import Annotated
from fastapi import Body, FastAPI, status
from pydantic_settings import BaseSettings

from src.model.commons.error import Error
from src.model.communications.comms.messager import MockedCommunicationsMessager, TwilioCommunicationsMessager
from src.model.communications.data.base import CommunicationsBase, RelCommunicationsBase
from src.model.communications.message import Message
from src.model.communications.service import CommunicationService, LocalCommunicationProvider
from src.model.communications.user import User


class Settings(BaseSettings):
    db_string: str
    dev: bool = False
    twilio_sid: str = ""
    twilio_token: str = ""

settings = Settings()

app = FastAPI()
comms = MockedCommunicationsMessager()
if not settings.dev: 
    comms = TwilioCommunicationsMessager(settings.twilio_sid, settings.twilio_token)
database = RelCommunicationsBase(settings.db_string) 
service = CommunicationService(
    LocalCommunicationProvider(
        database,
        comms
    )
)

@app.post("/user", responses={status.HTTP_400_BAD_REQUEST: {"model": Error}})
async def store_user(user: Annotated[User, Body()]):
    return await service.store_user(user)

@app.post("/messages", responses={status.HTTP_400_BAD_REQUEST: {"model": Error}})
async def send_message(message: Annotated[Message, Body()]):
    return await service.send_message(message)