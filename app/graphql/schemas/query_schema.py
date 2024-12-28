from datetime import datetime, timedelta
from typing import Optional

import strawberry
from bson import ObjectId
from fastapi import HTTPException, status

from app.auth.JWTBearer import IsAuthenticated
from app.core.db import db
from app.graphql.resolvers.chats_resolver import get_chats_pagination_window
from app.graphql.resolvers.ia_resolver import get_models_pagination_window
from app.graphql.resolvers.messages_resolver import (
    get_favs_msgs_pagination_window,
    get_guest_msgs_pagination_window,
    get_msgs_pagination_window,
)
from app.graphql.resolvers.reminders_resolver import (
    get_reminders_pagination_window,
    getReminder,
)
from app.graphql.resolvers.users_resolver import get_pagination_window, getCurrentUser
from app.graphql.types.paginationWindow import PaginationWindow
from app.models.chat import ChatType
from app.models.ia_model import IamodelType
from app.models.message import MessageType
from app.models.reminder import ReminderType
from app.models.user import UserType


@strawberry.type
class Query:
    @strawberry.field(description=" Print Hello World Just For meh")
    async def hello_world(self) -> str:
        return "HelloWorld"

    @strawberry.field(description="Get a user by id")
    async def get_user_by_id(self, id: str) -> UserType:
        user = db["users"].find_one({"_id": ObjectId(id)})
        if user:
            user["id"] = str(user.pop("_id"))
            return UserType(**user)
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

    @strawberry.field(description="Get a user by email")
    async def get_user_by_email(self, email: str) -> UserType:
        user = db["users"].find_one({"email": email})
        if user:
            user["id"] = str(user.pop("_id"))
            return UserType(**user)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    @strawberry.field(
        permission_classes=[IsAuthenticated],
        description="Bring data about the current user",
    )
    async def me(self, info) -> UserType | None:
        if "Authorization" not in info.context["request"].headers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not authenticated",
            )

        if (
            info.context["request"].headers["Authorization"].split("Bearer ")[-1]
            is None
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not authenticated",
            )
        token = info.context["request"].headers["Authorization"].split("Bearer ")[-1]
        user = getCurrentUser(token)
        return user

    @strawberry.field(description="Get a list of users.")
    async def get_all_users(
        self,
        order_by: str,
        limit: int,
        offset: int = 0,
        desc: bool = False,
    ) -> PaginationWindow[UserType]:
        return await get_pagination_window(
            dataset="users",
            ItemType=UserType,
            order_by=order_by,
            limit=limit,
            offset=offset,
            desc=desc,
        )

    @strawberry.field(
        description="Get a list of Reminders by user",
        permission_classes=[IsAuthenticated],
    )
    async def get_all_reminders(
        self,
        info,
        order_by: str,
        limit: int,
        offset: int = 0,
        desc: bool = False,
    ) -> PaginationWindow[ReminderType]:
        if "Authorization" not in info.context["request"].headers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not authenticated",
            )

        if (
            info.context["request"].headers["Authorization"].split("Bearer ")[-1]
            is None
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not authenticated",
            )
        token = info.context["request"].headers["Authorization"].split("Bearer ")[-1]
        return await get_reminders_pagination_window(
            dataset="reminders",
            ItemType=ReminderType,
            order_by=order_by,
            limit=limit,
            offset=offset,
            desc=desc,
            token=token,
        )

    @strawberry.field(
        description="Get a reminder by id", permission_classes=[IsAuthenticated]
    )
    async def get_reminder_by_id(self, id: str, info) -> ReminderType:
        if "Authorization" not in info.context["request"].headers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not authenticated",
            )

        if (
            info.context["request"].headers["Authorization"].split("Bearer ")[-1]
            is None
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not authenticated",
            )
        token = info.context["request"].headers["Authorization"].split("Bearer ")[-1]
        return await getReminder(id, token)

    @strawberry.field(
        description="Get a list of chats by user", permission_classes=[IsAuthenticated]
    )
    async def get_all_chats(
        self,
        info,
        order_by: str,
        limit: int,
        offset: Optional[int] = 0,
        desc: Optional[bool] = False,
    ) -> PaginationWindow[ChatType]:
        if "Authorization" not in info.context["request"].headers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not authenticated",
            )

        if (
            info.context["request"].headers["Authorization"].split("Bearer ")[-1]
            is None
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not authenticated",
            )
        token = info.context["request"].headers["Authorization"].split("Bearer ")[-1]
        return await get_chats_pagination_window(
            dataset="chats",
            ItemType=ChatType,
            order_by=order_by,
            limit=limit,
            offset=offset,
            desc=desc,
            token=token,
        )

    @strawberry.field(
        description="Get a list of messages by chat",
        permission_classes=[IsAuthenticated],
    )
    async def get_all_messages(
        self,
        info,
        order_by: str,
        limit: int,
        chat_id: str,
        offset: Optional[int] = 0,
        desc: Optional[bool] = False,
    ) -> PaginationWindow[MessageType]:
        if "Authorization" not in info.context["request"].headers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not authenticated",
            )

        if (
            info.context["request"].headers["Authorization"].split("Bearer ")[-1]
            is None
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not authenticated",
            )
        token = info.context["request"].headers["Authorization"].split("Bearer ")[-1]
        return await get_msgs_pagination_window(
            dataset="messages",
            ItemType=MessageType,
            order_by=order_by,
            limit=limit,
            offset=offset,
            desc=desc,
            token=token,
            chat_id=chat_id,
        )

    @strawberry.field(description="Get a list of favorite messages")
    async def get_all_favorite_messages(
        self,
        info,
        order_by: str,
        limit: int,
        offset: int = 0,
        desc: bool = True,
    ) -> PaginationWindow[MessageType]:
        if "Authorization" not in info.context["request"].headers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not authenticated",
            )
        if (info.context["request"].headers["Authorization"].split("Bearer ")[-1] is None):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not authenticated",
            )
        token = info.context["request"].headers["Authorization"].split("Bearer ")[-1]
        return await get_favs_msgs_pagination_window(
            dataset="messages",
            ItemType=MessageType,
            order_by=order_by,
            limit=limit,
            offset=offset,
            desc=desc,
            token=token,
        )

    @strawberry.field(description="Get a list of IA models")
    async def get_all_ia_models(
        self,
        order_by: str,
        limit: int,
        offset: int = 0,
        desc: bool = False,
    ) -> PaginationWindow[IamodelType]:
        return await get_models_pagination_window(
            dataset="models",
            ItemType=IamodelType,
            order_by=order_by,
            limit=limit,
            offset=offset,
            desc=desc,
        )

    @strawberry.field(description="Get popular guest queries")
    async def get_popular_queries(
        self, days: int = 7, limit: int = 10
    ) -> list[str]:
        cutoff_date = datetime.now() - timedelta(days=days)
        pipeline = [
            {"$match": {"created_at": {"$gte": cutoff_date}}},
            {"$group": {"_id": "$content", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": limit},
        ]

        results = list(db["guest_messages"].aggregate(pipeline))
        return [r["_id"] for r in results]

    @strawberry.field(description="Get messages from a chat (authenticated or guest)")
    async def get_chat_messages(
        self,
        info,
        order_by: str,
        limit: int,
        chat_id: str,
        session_id: Optional[str] = None,  # Para invitados
        offset: Optional[int] = 0,
        desc: Optional[bool] = False,
    ) -> PaginationWindow[MessageType]:
        # Si hay token de autenticación, usar el método existente
        if "Authorization" in info.context["request"].headers:
            token = info.context["request"].headers["Authorization"].split("Bearer ")[-1]
            return await get_msgs_pagination_window(
                dataset="messages",
                ItemType=MessageType,
                order_by=order_by,
                limit=limit,
                offset=offset,
                desc=desc,
                token=token,
                chat_id=chat_id,
            )

        # Si hay session_id, usar el método para invitados
        return await get_guest_msgs_pagination_window(
            dataset="messages",
            ItemType=MessageType,
            order_by=order_by,
            limit=limit,
            offset=offset,
            desc=desc,
            chat_id=chat_id,
            session_id=session_id,
        )

        # Si no hay ni token ni session_id
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication or guest session required",
        )
