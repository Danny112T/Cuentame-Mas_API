import strawberry
from typing import Optional


@strawberry.input
class CreateUserInput:
    name: str
    lastname: str
    email: str
    password: str


@strawberry.input
class UpdateUserInput:
    email: str
    name: Optional[str] = None
    lastname: Optional[str] = None
    regimenFiscal: Optional[str] = None
    password: Optional[str] = None


@strawberry.input
class loginInput:
    email: str
    password: str
