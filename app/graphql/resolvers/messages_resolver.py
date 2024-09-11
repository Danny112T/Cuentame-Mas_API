from app.graphql.types.paginationWindow import PaginationWindow
from app.graphql.schemas.input_schema import CreateMessageInput
from app.models.message import MessageType, Rated, Role
from app.auth.JWTManager import JWTManager
from pymongo import DESCENDING, ASCENDING
from fastapi import HTTPException, status
from datetime import datetime
from app.core.db import db
from bson import ObjectId

from mlx_lm.utils import load, generate
import torch

model, tokenizer = load("./original_models/Meta-Llama-3.1-8B-Instruct-bf16/")


def generate_response(content: str, chat_id: str, max_length: int = 512) -> str:
    conversation = list(
        db["messages"].find({"chat_id": chat_id}).sort("created_at", DESCENDING)
    )
    messages = []
    if len(conversation) == 0:
        messages.append({"role": "user", "content": content})
    else:
        for message in conversation:
            messages.append({"role": message["role"], "content": message["content"]})
        messages.append({"role": "user", "content": content})

    prompt = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )

    return generate(model, tokenizer, prompt, max_tokens=max_length)


def makeMessageDict(input: CreateMessageInput) -> dict:
    return {
        "chat_id": input.chat_id,
        "role": input.role.value,
        "content": input.content,
        "iamodel_id": None,
        "bookmark": False,
        "rated": Rated.EMPTY.value,
        "created_at": datetime.now(),
    }


def makeMessageIaDict(input: CreateMessageInput, ia_response: str) -> dict:
    return {
        "chat_id": input.chat_id,
        "role": Role.IA.value,
        "content": ia_response,
        "bookmark": False,
        "rated": Rated.EMPTY.value,
        "created_at": datetime.now(),
    }


async def get_msgs_pagination_window(
    token: str,
    dataset: str,
    ItemType: type,
    order_by: str,
    limit: int,
    offset: int,
    desc: bool,
    chat_id: str,
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

    for x in db[dataset].find({"chat_id": chat_id}).sort(order_by, order_type):
        x["id"] = str(x.pop("_id"))
        data.append(ItemType(**x))

    total_items_count = db[dataset].count_documents({"chat_id": chat_id})

    if offset != 0 and not 0 <= offset < db[dataset].count_documents({}):
        raise Exception(
            f"offset ({offset}) is out of range " f"(0-{total_items_count - 1})"
        )

    data = data[offset : offset + limit]

    return PaginationWindow(items=data, total_items_count=total_items_count)


async def createMessage(input: CreateMessageInput, token: str):
    user_info = JWTManager.verify_jwt(token)
    if user_info is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if input.role.value == Role.USER.value:
        ai_response = generate_response(input.content, input.chat_id)

        user_message_dict = makeMessageDict(input)
        message = db["messages"].insert_one(user_message_dict)

        ai_message_dict = makeMessageIaDict(input, ai_response)
        ia_message = db["messages"].insert_one(ai_message_dict)

        if message.acknowledged and ia_message.acknowledged:
            message = db["messages"].find_one({"_id": message.inserted_id})
            ia_message = db["messages"].find_one({"_id": ia_message.inserted_id})
            if (message is not None) or (ia_message is not None):
                updated_result = db["chats"].update_one(
                    {"_id": ObjectId(input.chat_id)},
                    {
                        "$push": {
                            "messages": str(message["_id"]),
                            "messages": str(ia_message["_id"]),
                        }
                    },
                )
            if updated_result.modified_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update chat with the messages",
                )
            message["id"] = str(message.pop("_id"))
            ia_message["id"] = str(ia_message.pop("_id"))

            return MessageType(**message), MessageType(**ia_message)

        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to send message",
            )
