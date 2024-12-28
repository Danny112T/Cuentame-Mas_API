from datetime import datetime
from enum import Enum

import strawberry
from pydantic import BaseModel, Field


@strawberry.enum
class Rated(Enum):
    EMPTY = "Empty"
    BAD = "Bad"
    GOOD = "Good"


@strawberry.enum
class Role(Enum):
    IA = "assistant"
    USER = "user"


class Message(BaseModel):
    id: str = Field(None, alias="_id")
    chat_id: str
    role: Role = Role.USER.value
    content: str
    bookmark: bool = False
    rated: Rated = Rated.EMPTY.value
    session_id: str | None = None
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


@strawberry.experimental.pydantic.type(model=Message)
class MessageType:
    id: strawberry.ID
    chat_id: str
    role: Role
    content: str
    bookmark: bool
    rated: Rated
    session_id: str | None = None
    created_at: datetime
    updated_at: datetime | None
