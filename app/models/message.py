import strawberry
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


@strawberry.enum
class Rated(Enum):
    EMPTY: str = "Empty"
    BAD: str = "Bad"
    GOOD: str = "Good"


@strawberry.enum
class Role(Enum):
    IA: str = "assistant"
    USER: str = "user"


class Message(BaseModel):
    id: str = Field(None, alias="_id")
    chat_id: str
    role: Role = Role.USER.value
    content: str
    iamodel_id: str | None = None
    bookmark: bool = False
    rated: Rated = Rated.EMPTY.value
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


@strawberry.experimental.pydantic.type(model=Message)
class MessageType:
    id: strawberry.ID
    chat_id: str
    iamodel_id: str | None
    role: Role
    content: str
    bookmark: bool
    rated: Rated
    created_at: datetime
    updated_at: datetime | None
