from datetime import datetime
from typing import List

import strawberry
from pydantic import BaseModel, Field

from app.models.message import MessageType


class Chat(BaseModel):
    id: str = Field(None, alias="_id")
    user_id: str | None = None
    session_id: str | None = None
    iamodel_id: str | None = None
    title: str
    created_at: datetime
    updated_at: datetime | None = None
    messages: List[str] = []

    class Config:
        from_attributes = True


@strawberry.experimental.pydantic.type(model=Chat)
class ChatType:
    id: strawberry.ID
    user_id: str | None
    session_id: str | None
    iamodel_id: str | None
    title: str
    created_at: str
    updated_at: str | None
    messages: List[MessageType]
