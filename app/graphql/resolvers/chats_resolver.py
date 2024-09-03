from app.graphql.types.paginationWindow import PaginationWindow
from app.graphql.schemas.input_schema import CreateChatInput, UpdateChatInput
from app.auth.JWTManager import JWTManager
from pymongo import DESCENDING, ASCENDING
from fastapi import HTTPException, status
from app.models.chat import ChatType
from app.core.db import db
from datetime import datetime
from bson import ObjectId


def makeChatDict(input: CreateChatInput) -> dict:
    return {
        "title": input.title,
        "created_at": datetime.now(),
        "updated_at": None,
    }

def updateChatDict(input: CreateChatInput) -> dict:
    return {
        "title": input.title,
        "updated_at": datetime.now(),
    }


async def createChat(input: CreateChatInput, token: str) -> ChatType:
    user_info = JWTManager.verify_jwt(token)
    if user_info is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    chat_dict = makeChatDict(input)

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
                    detail="Failed to update user with chat",
                )
            chat["id"] = str(chat.pop("_id"))
            return ChatType(**chat)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve inserted chat",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to insert chat",
        )


async def get_chats_pagination_window(
    token: str,
    dataset: str,
    ItemType: type,
    order_by: str,
    limit: int,
    offset: int = 0,
    desc: bool = False,
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

    data = []
    order_type = DESCENDING if desc else ASCENDING
    if limit <= 0 or limit > 100:
        raise Exception(f"limit ({limit}) must be between 0-100")

    for x in db[dataset].find({"user_id": user_info["sub"]}).sort(order_by, order_type):
        x["id"] = str(x.pop("_id"))
        data.append(ItemType(**x))

    total_items_count = db[dataset].count_documents({"user_id": user_info["sub"]})

    if offset != 0 and not 0 <= offset < db[dataset].count_documents({}):
        raise Exception(
            f"offset ({offset}) is out of range " f"(0-{total_items_count - 1})"
        )

    data = data[offset : offset + limit]

    return PaginationWindow(items=data, total_items_count=total_items_count)

async def updateChat(input: UpdateChatInput, token: str) -> ChatType:
    user_info = JWTManager.verify_jwt(token)
    if user_info is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    chat = db["chats"].find_one({"_id": ObjectId(input.id)})
    if chat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found",
        )

    if chat["user_id"] != user_info["sub"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update this chat",
        )

    chat_dict = updateChatDict(input)

    update_result = db["chats"].update_one(
        {"_id": ObjectId(input.id)},
        {"$set": chat_dict},
        upsert=False,
    )

    if update_result.matched_count == 1:
        updated_chat = db["chats"].find_one({"_id": ObjectId(input.id)})
        updated_chat["id"] = str(updated_chat.pop("_id"))
        return ChatType(**updated_chat)
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update chat",
        )

async def deleteChat(id: str, token: str) -> ChatType:
    user_info = JWTManager.verify_jwt(token)
    if user_info is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    chat = db["chats"].find_one({"_id": ObjectId(id)})
    if chat is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat not found",
        )

    if chat["user_id"] != user_info["sub"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this chat",
        )

    delete_result = db["chats"].delete_one({"_id": ObjectId(id)})

    if delete_result.deleted_count == 1:
        chat["id"] = str(chat.pop("_id"))
        return ChatType(**chat)
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete chat",
        )
