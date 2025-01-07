from datetime import datetime
from enum import Enum

import strawberry
from pydantic import BaseModel, Field

from app.models.chat import ChatType


@strawberry.enum
class GuestSessionStatus(Enum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"

class GuestSession (BaseModel):
    id: str = Field(None, alias="_id")
    session_id: str
    created_at: datetime
    chat_id: str
    status: GuestSessionStatus = GuestSessionStatus.ACTIVE.value

    class Config:
        from_attributes = True


@strawberry.experimental.pydantic.type(model=GuestSession)
class GuestSessionType:
    id: strawberry.ID
    session_id: str
    created_at: datetime
    chat_id: ChatType
    status: GuestSessionStatus
