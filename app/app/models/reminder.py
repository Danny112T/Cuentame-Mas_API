import strawberry
from datetime import datetime
from pydantic import BaseModel, Field


class Reminder(BaseModel):
    id: str = Field(None, alias="_id")
    user_id: str
    title: str
    description: str | None = None
    finishDate: datetime
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


@strawberry.experimental.pydantic.type(model=Reminder, all_fields=True)
class ReminderType:
    pass
