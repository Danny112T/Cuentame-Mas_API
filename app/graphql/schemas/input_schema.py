from datetime import datetime
from typing import Optional

import strawberry

from app.models.message import Rated, Role
from app.models.user import RegimenFiscal

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
    regimenFiscal: Optional[RegimenFiscal] = None
    old_password: Optional[str] = None
    new_password: Optional[str] = None

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
    iamodel_id: Optional[str] = None


@strawberry.input
class UpdateChatInput:
    id: str
    title: Optional[str] = None
    iamodel_id: Optional[str] = None


"""
Messages Input
"""


@strawberry.input
class CreateMessageInput:
    chat_id: str
    content: str
    role: Role


@strawberry.input
class UpdateMessageInput:
    message_id: str
    bookmark: Optional[bool] = None
    rated: Optional[Rated] = None


@strawberry.input
class RegenerateMessageInput:
    user_message_id: str
    iamodel_message_id: str
    content: str


@strawberry.input
class DeleteMessageInput:
    user_message_id: str
    iamodel_message_id: str


"""
IA Models Input
"""


@strawberry.input
class RegisterIaModelInput:
    name: str
    algorithm: str
    params: str
    description: str
    path: str


@strawberry.input
class UpdateIaModelInput:
    id: str
    name: Optional[str] = None
    algorithm: Optional[str] = None
    params: Optional[str] = None
    description: Optional[str] = None
    path: Optional[str] = None


@strawberry.input
class DeleteIaModelInput:
    id: str
