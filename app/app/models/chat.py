import strawberry
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List
from app.models.message import MessageType


class Chat(BaseModel):
    id: str = Field(None, alias="_id")
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime | None = None
    messages: List[str] = []

    class Config:
        from_attributes = True


@strawberry.experimental.pydantic.type(model=Chat)
class ChatType:
    id: strawberry.ID
    user_id: str
    title: str
    created_at: str
    updated_at: str | None
    messages: List[MessageType]
