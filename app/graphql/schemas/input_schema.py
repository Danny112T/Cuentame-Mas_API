import strawberry
from typing import Optional
from datetime import datetime

"""
Users Input
"""


@strawberry.input
class CreateUserInput:
    name: str
    lastname: str
    email: str
    password: str


@strawberry.input
class UpdateUserInput:
    email: Optional[str] = None
    name: Optional[str] = None
    lastname: Optional[str] = None
    regimenFiscal: Optional[str] = None
    password: Optional[str] = None


@strawberry.input
class loginInput:
    email: str
    password: str


"""
Reminders Input
"""


@strawberry.input
class CreateReminderInput:
    title: str
    description: Optional[str] = None
    finishDate: datetime


@strawberry.input
class UpdateReminderInput:
    id: str
    title: Optional[str] = None
    description: Optional[str] = None
    finishDate: Optional[datetime] = None


"""
Chats Input
"""


@strawberry.input
class CreateChatInput:
    title: str

@strawberry.input
class UpdateChatInput:
    id: str
    title: str
