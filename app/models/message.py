import strawberry
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


@strawberry.enum
class Rated(Enum):
    NO: str = "No"
    BAD: str = "Bad"
    GOOD: str = "Good"


@strawberry.enum
class MsgFrom(Enum):
    IA: str = "iaMsg"  #
    USER: str = "userMsg"  # va x default


class Message(BaseModel):
    id: str = Field(None, alias="_id")
    chat_id: str
    msg_from: MsgFrom = MsgFrom.USER.value
    text: str
    iamodel_id: str
    bookmark: bool = False
    rated: Rated = Rated.NO.value
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


@strawberry.experimental.pydantic.type(model=Message)
class MessageType:
    id: strawberry.ID
    chat_id: str
    iamodel_id: str
    msg_from: MsgFrom
    text: str
    bookmark: bool
    rated: Rated
    created_at: datetime
    updated_at: datetime | None
