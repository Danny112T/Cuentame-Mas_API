import strawberry
from typing import Optional
from src.graphql.models.user import RegimenFiscal


@strawberry.input
class CreateUserInput:
    name: str
    lastname: str
    email: str
    password: str


@strawberry.input
class UpdateUserInput:
    name: Optional[str] = strawberry.unset
    lastname: Optional[str] = strawberry.unset
    custom_instruction: Optional[str] = strawberry.unset
    age: Optional[int] = strawberry.unset
    regimenFiscal: Optional[str] = strawberry.unset
    password: Optional[str] = strawberry.unset


@strawberry.input
class loginInput:
    email: str
    password: str
