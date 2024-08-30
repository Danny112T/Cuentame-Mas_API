import strawberry
from enum import Enum
from typing import List
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.reminder import ReminderType
from app.models.chat import ChatType


@strawberry.enum
class RegimenFiscal(Enum):
    NO_DEFINIDO: str = "NoDefinido"


class User(BaseModel):
    id: str = Field(None, alias="_id")
    name: str
    lastname: str
    email: str
    regimenFiscal: RegimenFiscal = RegimenFiscal.NO_DEFINIDO.value
    password: str
    created_at: datetime
    updated_at: datetime | None = None
    reminders: List[str] = []
    chats: List[str] = []

    class Config:
        from_attributes = True


@strawberry.experimental.pydantic.type(model=User)
class UserType:
    id: strawberry.ID
    name: str
    lastname: str
    email: str
    regimenFiscal: RegimenFiscal
    password: str
    created_at: datetime
    updated_at: datetime | None
    reminders: List[ReminderType]
    chats: List[ChatType]


class Token(BaseModel):
    access_token: str
    token_type: str


@strawberry.experimental.pydantic.type(model=Token, all_fields=True)
class TokenType:
    pass
