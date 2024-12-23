from datetime import datetime
from typing import Optional

import strawberry
from pydantic import BaseModel, Field

from app.models.chat import ChatType


class GuestSession (BaseModel):
    id: str = Field(None, alias="_id")
    session_id: str
    created_at: datetime
    chats: list[str] = []

    class Config:
        from_attributes = True


@strawberry.experimental.pydantic.type(model=GuestSession)
class GuestSessionType:
    id: strawberry.ID
    session_id: str
    created_at: datetime
    chats: list[ChatType]
