import strawberry
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum
from typing import List
from app.models.reminder import ReminderType


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


class Token(BaseModel):
    access_token: str
    token_type: str


@strawberry.experimental.pydantic.type(model=Token, all_fields=True)
class TokenType:
    pass
