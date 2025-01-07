import uuid
from datetime import datetime

from bson import ObjectId
from fastapi import HTTPException, status

from app.core.db import db
from app.models.chat import ChatType
from app.models.guest_session import GuestSessionStatus, GuestSessionType


async def create_guest_session() -> GuestSessionType:
    session_id = str(uuid.uuid4())

    guest_chat = {
        "session_id": session_id,
        "title": "Chat de invitado",
        "iamodel_id": "677ccb0504bf6dc0e97b54b9",
        "created_at": datetime.now(),
        "messages": []
    }

    chat_result = db["chats"].insert_one(guest_chat)
    if not chat_result.acknowledged:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear el chat de invitado",
        )

    guest_session = {
        "session_id": session_id,
        "created_at": datetime.now(),
        "chat_id": str(chat_result.inserted_id),
        "status": GuestSessionStatus.ACTIVE.value

    }
    session_result = db["guest_sessions"].insert_one(guest_session)
    if session_result.acknowledged:
        chat = db["chats"].find_one({"_id": ObjectId(chat_result.inserted_id)})
        chat["id"] = str(chat.pop("_id"))
        response_data = {
            "id": str(session_result.inserted_id),
            "session_id": session_id,
            "created_at": guest_session["created_at"],
            "chat_id": ChatType(**chat),
        }

        return GuestSessionType(**response_data)

    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al crear la sesión de invitado")

async def validate_guest_session(session_id: str) -> bool:
    session = db["guest_sessions"].find_one({"session_id": session_id, "status": "ACTIVE"})
    return session is not None
