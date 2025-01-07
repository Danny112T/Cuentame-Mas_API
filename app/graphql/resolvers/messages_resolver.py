
import uuid
from datetime import datetime

from bson import ObjectId
from fastapi import HTTPException, status
from pymongo import ASCENDING, DESCENDING

from app.auth.JWTManager import JWTManager
from app.core.db import db
from app.graphql.resolvers.guest_resolver import validate_guest_session
from app.graphql.resolvers.ia_resolver import generate_response
from app.graphql.schemas.input_schema import (
    CreateGuestMessageInput,
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
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user_info["sub"] != db["chats"].find_one({"_id":ObjectId(chat_id)}).get("user_id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes autorización para ver estos mensajes",
        )

    data = []
    order_type = DESCENDING if desc else ASCENDING
    if limit <= 0 or limit > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El limite ({limit}) debe estar entre 0-100",
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
            detail=f"El offset ({offset}) está fuera fuera de rango (0-{total_items_count -1 })",
        )

    data = data[offset : offset + limit]

    return PaginationWindow(items=data, total_items_count=total_items_count)


async def get_favs_msgs_pagination_window(
    token: str,
    dataset: str,
    order_by: str,
    limit: int,
    offset: int,
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
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = user_info["sub"]
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    data = []
    order_type = DESCENDING if desc else ASCENDING
    order_by = "created_at" if order_by is None else order_by

    if limit <= 0 or limit > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El limite ({limit}) debe estar entre 0-100",
        )


    for x in db["chats"].find({"user_id": user_id}):
        for y in db[dataset].find({"chat_id": str(x["_id"]), "bookmark":True}).sort(order_by, order_type):
            y["id"] = str(y.pop("_id"))
            data.append(ItemType(**y))


    total_items_count = len(data)
    if total_items_count == 0:
        return PaginationWindow(items=data, total_items_count=total_items_count)

    if offset != 0 and not 0 <= offset < db[dataset].count_documents({}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El offset ({offset}) esta fuera de rango (0-{total_items_count -1 })",
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
            detail="Credenciales inválidas",
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
            detail="Error al actualizar el chat con los mensajes",
        )

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Error al enviar el mensaje",
    )


async def delete_message(input: DeleteMessageInput, token: str) -> tuple[MessageType, MessageType]:
    user_info = JWTManager.verify_jwt(token)
    if user_info is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_message = db["messages"].find_one({"_id": ObjectId(input.user_message_id)})
    iamodel_message = db["messages"].find_one({"_id": ObjectId(input.iamodel_message_id)})
    usr_message_deleted = db["messages"].delete_one({"_id": ObjectId(input.user_message_id)})
    ia_message_deleted = db["messages"].delete_one({"_id": ObjectId(input.iamodel_message_id)})

    if usr_message_deleted.deleted_count == 0 or ia_message_deleted.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al eliminar el mensaje",
        )

    return MessageType(**user_message), MessageType(**iamodel_message)


async def update_message(input: UpdateMessageInput, token: str) -> MessageType | None:
    user_info = JWTManager.verify_jwt(token)
    if user_info is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if input.message_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Faltan campos obligatorios",
        )

    message = db["messages"].find_one({"_id": ObjectId(input.message_id)})
    if message is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mensaje no encontrado",
        )
    rated = input.rated.value if input.rated is not None else message.get("rated")
    bookmark = input.bookmark if input.bookmark is not None else message.get("bookmark")

    message = db["messages"].update_one(
        {"_id": ObjectId(input.message_id)},
        {"$set": {
            "rated":rated,
            "bookmark": bookmark,
            "updated_at": datetime.now()}
        },
        upsert= False,
    )

    if message.matched_count == 1:
        updated_message = db["messages"].find_one({"_id": ObjectId(input.message_id)})
        updated_message["id"] = str(updated_message.pop("_id"))
        idchat = db["messages"].find_one({"_id":ObjectId(input.message_id)}).get("chat_id")
        db["chats"].update_one(
            {"_id":ObjectId(idchat)},
            {"$set": {"updated_at": datetime.now()}},
            upsert= False,
        )
        return MessageType(**updated_message)

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Error al actualizar el mensaje",
    )


async def regenerate_message(input: RegenerateMessageInput, token: str) -> tuple[MessageType, MessageType] | None:
    user_info = JWTManager.verify_jwt(token)
    if user_info is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if input.content is None and input.user_message_id is None and input.iamodel_message_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Faltan campos obligatorios",
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
            detail="Error al actualizar los mensajes",
    )

    updated_usr = db["messages"].find_one({"_id":ObjectId(input.user_message_id)})
    updated_ia = db["messages"].find_one({"_id":ObjectId(input.iamodel_message_id)})

    updated_usr["id"] = str(updated_usr.pop("_id"))
    updated_ia["id"] = str(updated_ia.pop("_id"))

    return MessageType(**updated_usr), MessageType(**updated_ia)


async def create_guest_message(input: CreateGuestMessageInput) -> tuple[MessageType,MessageType]:
    if not await validate_guest_session(input.session_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Id de sesión de invitado inválido",
        )

    chat_id = db["guest_sessions"].find_one({"session_id":input.session_id}).get("chat_id")
    model_id = db["chats"].find_one({"_id":ObjectId(chat_id)}).get("iamodel_id")
    ai_response = generate_response(input.content, chat_id, model_id)

    user_guest_message = {
        "session_id": input.session_id,
        "chat_id": chat_id,
        "content": input.content,
        "role": Role.USER.value,
        "created_at": datetime.now(),
    }
    user_msg_result = db["guest_messages"].insert_one(user_guest_message)
    ai_message = {
        "session_id": input.session_id,
        "chat_id": chat_id,
        "content": ai_response,
        "role": Role.IA.value,
        "created_at": datetime.now(),
    }
    ai_msg_result = db["guest_messages"].insert_one(ai_message)

    if user_msg_result.acknowledged and ai_msg_result.acknowledged:
        db["chats"].update_one(
            {"session_id": input.session_id},
            {
                "$push": {
                    "messages": {
                        "$each": [
                            str(user_msg_result.inserted_id),
                            str(ai_msg_result.inserted_id),
                        ]
                    },
                },
                "$set": {"updated_at": datetime.now()},
            },
        )
        return (
            MessageType(
                id=str(user_msg_result.inserted_id),
                chat_id=chat_id,
                role=Role.USER,
                content=input.content,
                created_at=datetime.now(),
            ),
            MessageType(
                id=str(ai_msg_result.inserted_id),
                chat_id=chat_id,
                role=Role.IA,
                content=ai_response,
                created_at=datetime.now(),
            ),
        )
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Error al crear el mensaje de invitado",
    )

async def get_guest_msgs_pagination_window(
    dataset: str,
    order_by: str,
    limit: int,
    offset: int,
    chat_id: str,
    session_id: str,
    desc: bool,
    ItemType: type,
) -> PaginationWindow:
    """
    Get messages pagination window for guest sessions
    """
    # Validar la sesión del invitado
    session = db["guest_sessions"].find_one({"session_id": session_id, "status": "ACTIVE"})
    if not session:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Sesión de invitado inválida",
        )

    # Verificar que el chat pertenece a la sesión
    chat = db["chats"].find_one({"_id": ObjectId(chat_id)})
    if not chat or chat.get("session_id") != session_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes autorización para ver estos mensajes",
        )

    data = []
    order_type = DESCENDING if desc else ASCENDING

    if limit <= 0 or limit > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El limite ({limit}) debe estar entre 0-100",
        )

    # Usar un diccionario para mantener mensajes únicos
    unique_messages = {}

    # Obtener mensajes de la colección regular
    for msg in db[dataset].find({"chat_id": chat_id}):
        msg_id = str(msg["_id"])
        msg["id"] = msg_id
        unique_messages[msg_id] = msg

    # Obtener mensajes de guest_messages
    for msg in db["guest_messages"].find({"chat_id": chat_id}):
        msg_id = str(msg["_id"])
        msg["id"] = msg_id
        unique_messages[msg_id] = msg

    # Convertir a lista y ordenar
    all_messages = list(unique_messages.values())
    all_messages.sort(
        key=lambda x: x[order_by],
        reverse=desc
    )

    # Actualizar el conteo total real
    total_items_count = len(all_messages)

    if total_items_count == 0:
        return PaginationWindow(items=[], total_items_count=0)

    # Aplicar paginación
    paginated_messages = all_messages[offset : offset + limit]

    # Formatear mensajes
    for msg in paginated_messages:
        if "_id" in msg:
            msg.pop("_id")  # Removemos _id ya que ya tenemos el id
        data.append(ItemType(**msg))

    return PaginationWindow(items=data, total_items_count=total_items_count)
