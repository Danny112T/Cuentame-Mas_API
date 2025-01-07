from datetime import datetime

from bson import ObjectId
from fastapi import HTTPException, status
from pymongo import ASCENDING, DESCENDING

from app.auth.JWTManager import JWTManager
from app.core.db import db
from app.graphql.schemas.input_schema import CreateChatInput, UpdateChatInput
from app.graphql.types.paginationWindow import PaginationWindow
from app.models.chat import ChatType
from app.models.message import MessageType


def make_chat_dict(input: CreateChatInput) -> dict:
    return {
        "title": input.title,
        "iamodel_id": input.iamodel_id,
        "created_at": datetime.now(),
        "updated_at": None,
    }


def update_chat_dict(input: UpdateChatInput) -> dict:
    chat = db["chats"].find_one({"_id": ObjectId(input.id)})
    if (input.title is not None) and (input.iamodel_id is not None):
        return {
            "title": input.title,
            "iamodel_id": input.iamodel_id,
            "updated_at": datetime.now(),
        }
    elif (input.title is not None) and (input.iamodel_id is None):
        return {
            "title": input.title,
            "iamodel_id": chat.get("iamodel_id"),
            "updated_at": datetime.now(),
        }
    elif (input.title is None) and (input.iamodel_id is not None):
        return {
            "title": chat.get("title"),
            "iamodel_id": input.iamodel_id,
            "updated_at": datetime.now(),
        }
    else:
        return {}


async def create_chat(input: CreateChatInput, token: str) -> ChatType:
    user_info = JWTManager.verify_jwt(token)
    if user_info is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    chat_dict = make_chat_dict(input)

    if input.iamodel_id is None:
        chat_dict["iamodel_id"] = "66ff79a6c3c7dfacdee54642"

    chat_dict["user_id"] = user_info["sub"]

    chat = db["chats"].insert_one(chat_dict)
    if chat.acknowledged:
        chat = db["chats"].find_one({"_id": chat.inserted_id})
        if chat:
            update_result = db["users"].update_one(
                {"_id": ObjectId(user_info["sub"])},
                {"$push": {"chats": str(chat["_id"])}},
            )
            if update_result.modified_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Error al actualizar el usuario con el chat",
                )
            chat["id"] = str(chat.pop("_id"))
            return ChatType(**chat)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error al recuperar el chat",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear el chat",
        )


async def get_chats_pagination_window(
    token: str,
    dataset: str,
    ItemType: type,
    order_by: str,
    limit: int,
    offset: int,
    desc: bool,
) -> PaginationWindow:
    """
    Get one pagination window on the given dataset for the given limit
    and offset, ordered by the given attribute and filtered using the
    given filters
    """

    user_info = JWTManager.verify_jwt(token)
    if user_info is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    data = []
    order_type = DESCENDING if desc else ASCENDING
    if limit <= 0 or limit > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"limit ({limit}) must be between 0-100",
        )

    for x in db[dataset].find({"user_id": user_info["sub"]}).sort(order_by, order_type):
        x["id"] = str(x.pop("_id"))
        messages = []
        for message in (
            db["messages"].find({"chat_id": x["id"]}).sort("created_at", ASCENDING)
        ):
            message["id"] = str(message.pop("_id"))
            messages.append(message)

        x["messages"] = [MessageType(**message) for message in messages]
        data.append(ItemType(**x))

    total_items_count = db[dataset].count_documents({"user_id": user_info["sub"]})

    if offset != 0 and not 0 <= offset < db[dataset].count_documents({}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El offset ({offset}) está fuera fuera de rango (0-{total_items_count -1 })",
        )
    data = data[offset : offset + limit]

    return PaginationWindow(items=data, total_items_count=total_items_count)


async def update_chat(input: UpdateChatInput, token: str) -> ChatType:
    user_info = JWTManager.verify_jwt(token)
    if user_info is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    chat = db["chats"].find_one({"_id": ObjectId(input.id)})
    if chat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat no encontrado",
        )

    if chat["user_id"] != user_info["sub"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes autorización para actualizar este chat",
        )

    chat_dict = update_chat_dict(input)

    if chat_dict is None:
        chat_dict["iamodel_id"] = chat.get("iamodel_id")
        chat_dict["title"] = chat.get("title")

    update_result = db["chats"].update_one(
        {"_id": ObjectId(input.id)},
        {"$set": chat_dict},
        upsert=False,
    )

    if update_result.matched_count == 1:
        updated_chat = db["chats"].find_one({"_id": ObjectId(input.id)})
        updated_chat["id"] = str(updated_chat.pop("_id"))
        return ChatType(**updated_chat)

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Error al actualizar el chat",
    )


async def delete_chat(id: str, token: str) -> ChatType:
    user_info = JWTManager.verify_jwt(token)
    if user_info is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    chat = db["chats"].find_one({"_id": ObjectId(id)})
    messages_data = []
    for messages in db["messages"].find({"chat_id": id}):
        messages["id"] = str(messages.pop("_id"))
        messages_data.append(messages)

    if chat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat no encontrado",
        )

    if chat["user_id"] != user_info["sub"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes autorización para eliminar este chat",
        )

    total_messages = db["messages"].count_documents({"chat_id": id})
    if total_messages != len(messages_data):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al recuperar los mensajes del chat",
        )

    deleted_messages_result = db["messages"].delete_many({"chat_id": id})
    delete_result = db["chats"].delete_one({"_id": ObjectId(id)})

    if (
        delete_result.deleted_count == 1
        and deleted_messages_result.deleted_count == total_messages
    ):
        chat["id"] = str(chat.pop("_id"))
        chat["messages"] = [MessageType(**message) for message in messages_data]
        return ChatType(**chat)

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Error al eliminar el chat",
    )
