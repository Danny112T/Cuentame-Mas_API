import strawberry
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


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

    class Config:
        from_attributes = True


@strawberry.experimental.pydantic.type(model=User, all_fields=True)
class UserType:
    pass


class Token(BaseModel):
    access_token: str
    token_type: str


@strawberry.experimental.pydantic.type(model=Token, all_fields=True)
class TokenType:
    pass
