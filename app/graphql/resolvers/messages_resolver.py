
from datetime import datetime

from bson import ObjectId
from fastapi import HTTPException, status
from pymongo import ASCENDING, DESCENDING

from app.auth.JWTManager import JWTManager
from app.core.db import db
from app.graphql.resolvers.ia_resolver import generate_response
from app.graphql.schemas.input_schema import (
    CreateMessageInput,
    DeleteMessageInput,
    RegenerateMessageInput,
    UpdateMessageInput,
)
from app.graphql.types.paginationWindow import PaginationWindow
from app.models.message import MessageType, Rated, Role


def make_message_dict(input: CreateMessageInput) -> dict:
    return {
        "chat_id": input.chat_id,
        "role": input.role.value,
        "content": input.content,
        "bookmark": False,
        "rated": Rated.EMPTY.value,
        "created_at": datetime.now(),
        "updated_at": None,
    }


def make_message_ia_dict(input: CreateMessageInput, ia_response: str) -> dict:
    return {
        "chat_id": input.chat_id,
        "role": Role.IA.value,
        "content": ia_response,
        "bookmark": False,
        "rated": Rated.EMPTY.value,
        "created_at": datetime.now(),
        "updated_at": None,
    }


async def get_msgs_pagination_window(
    token: str,
    dataset: str,
    order_by: str,
    limit: int,
    offset: int,
    chat_id: str,
    desc: bool,
    ItemType: type,
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
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user_info["sub"] != db["chats"].find_one({"_id":ObjectId(chat_id)}).get("user_id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to see this mesages",
        )

    data = []
    order_type = DESCENDING if desc else ASCENDING
    if limit <= 0 or limit > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"limit ({limit}) must be between 0-100",
        )

    total_items_count = db[dataset].count_documents({"chat_id": chat_id})
    if total_items_count == 0:
        return PaginationWindow(items=data, total_items_count=total_items_count)

    for x in db[dataset].find({"chat_id": chat_id}).sort(order_by, order_type):
        x["id"] = str(x.pop("_id"))
        data.append(ItemType(**x))


    if offset != 0 and not 0 <= offset < db[dataset].count_documents({}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"offset ({offset}) is out of range (0-{total_items_count -1 })",
        )

    data = data[offset : offset + limit]

    return PaginationWindow(items=data, total_items_count=total_items_count)


async def create_message(
    input: CreateMessageInput, token: str
) -> tuple[MessageType, MessageType]:
    user_info = JWTManager.verify_jwt(token)
    if user_info is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    model_id = db["chats"].find_one({"_id": ObjectId(input.chat_id)})["iamodel_id"]

    ai_response = generate_response(input.content, input.chat_id, model_id)

    user_message_dict = make_message_dict(input)
    message = db["messages"].insert_one(user_message_dict)

    ai_message_dict = make_message_ia_dict(input, ai_response)
    ia_message = db["messages"].insert_one(ai_message_dict)

    if message.acknowledged and ia_message.acknowledged:
        message = db["messages"].find_one({"_id": message.inserted_id})
        ia_message = db["messages"].find_one({"_id": ia_message.inserted_id})
        if (message is not None) or (ia_message is not None):
            updated_result1 = db["chats"].update_one(
                {"_id": ObjectId(input.chat_id)},
                {
                    "$push": {
                        "messages": {"$each": [str(message["_id"]), str(ia_message["_id"])]},
                    },
                    "$set": {
                        "updated_at": datetime.now(),
                    },
                },
            )
        if updated_result1.modified_count == 1:
            message["id"] = str(message.pop("_id"))
            ia_message["id"] = str(ia_message.pop("_id"))

            return MessageType(**message), MessageType(**ia_message)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update chat with the messages",
        )

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to send message",
    )


async def delete_message(input: DeleteMessageInput, token: str) -> tuple[MessageType, MessageType]:
    user_info = JWTManager.verify_jwt(token)
    if user_info is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_message = db["messages"].find_one({"_id": ObjectId(input.user_message_id)})
    iamodel_message = db["messages"].find_one({"_id": ObjectId(input.iamodel_message_id)})
    usr_message_deleted = db["messages"].delete_one({"_id": ObjectId(input.user_message_id)})
    ia_message_deleted = db["messages"].delete_one({"_id": ObjectId(input.iamodel_message_id)})

    if usr_message_deleted.deleted_count == 0 or ia_message_deleted.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete message",
        )

    return MessageType(**user_message), MessageType(**iamodel_message)


async def update_message(input: UpdateMessageInput, token: str) -> MessageType | None:
    user_info = JWTManager.verify_jwt(token)
    if user_info is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if input.rated is None and input.bookmark is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required fields",
        )

    value = "bookmark" if input.bookmark is not None else "rated"
    message_id = input.user_message_id or input.iamodel_message_id
    message = db["messages"].update_one(
        {"_id": ObjectId(message_id)},
        {"$set": {
            value: bool(input.bookmark) if input.bookmark is not None else input.rated.value,
            "updated_at": datetime.now()}
        },
        upsert= False,
    )

    if message.matched_count == 1:
        updated_message = db["messages"].find_one({"_id": ObjectId(message_id)})
        updated_message["id"] = str(updated_message.pop("_id"))
        idchat = db["messages"].find_one({"_id":ObjectId(input.user_message_id)}).get("chat_id")
        db["chats"].update_one(
            {"_id":ObjectId(idchat)},
            {"$set": {"updated_at": datetime.now()}},
            upsert= False,
        )
        return MessageType(**updated_message)

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Failed to update message",
    )

async def regenerate_message(input: RegenerateMessageInput, token: str) -> tuple[MessageType, MessageType] | None:
    user_info = JWTManager.verify_jwt(token)
    if user_info is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if input.content is None and input.user_message_id is None and input.iamodel_message_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required fields",
        )

    idchat = db["messages"].find_one({"_id":ObjectId(input.user_message_id)}).get("chat_id")
    idmodel = db["chats"].find_one({"_id":ObjectId(idchat)}).get("model_id")
    ia_response = generate_response(input.content, idchat, idmodel)

    updated_user_message = db["messages"].update_one(
        {"_id":ObjectId(input.user_message_id)},
        {"$set": {"content": input.content, "updated_at": datetime.now()}},
        upsert= False,
    )
    updated_ia_message = db["messages"].update_one(
        {"_id":ObjectId(input.iamodel_message_id)},
        {"$set": {"content": ia_response, "updated_at": datetime.now()}},
        upsert= False,
    )
    if updated_user_message.matched_count == 0 or updated_ia_message.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update messages",
    )

    updated_usr = db["messages"].find_one({"_id":ObjectId(input.user_message_id)})
    updated_ia = db["messages"].find_one({"_id":ObjectId(input.iamodel_message_id)})

    updated_usr["id"] = str(updated_usr.pop("_id"))
    updated_ia["id"] = str(updated_ia.pop("_id"))

    return MessageType(**updated_usr), MessageType(**updated_ia)
