import uuid
from datetime import datetime

from fastapi import HTTPException, status

from app.core.db import db
from app.models.guest_session import GuestSessionType


async def create_guest_session() -> GuestSessionType:
    session_id = str(uuid.uuid4())

    guest_session = {
        "session_id": session_id,
        "created_at": datetime.now(),
        "chats": []
    }

    result = db["guest_sessions"].insert_one(guest_session)
    if result.acknowledged:
        guest_session["id"] = str(guest_session.pop("_id"))
        return GuestSessionType(**guest_session)

    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating guest session")

async def validate_guest_session(session_id: str) -> bool:
    session = db["guest_sessions"].find_one({"session_id": session_id})
    return session is not None
