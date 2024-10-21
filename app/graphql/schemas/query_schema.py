from typing import Optional

import strawberry
from bson import ObjectId
from fastapi import HTTPException, status

from app.auth.JWTBearer import IsAuthenticated
from app.core.db import db
from app.graphql.resolvers.chats_resolver import get_chats_pagination_window
from app.graphql.resolvers.ia_resolver import get_models_pagination_window
from app.graphql.resolvers.messages_resolver import get_msgs_pagination_window
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
    async def helloWorld(self) -> str:
        return "HelloWorld"

    @strawberry.field(description="Get a user by id")
    async def getUserbyId(self, id: str) -> UserType:
        user = db["users"].find_one({"_id": ObjectId(id)})
        if user:
            user["id"] = str(user.pop("_id"))
            return UserType(**user)
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

    @strawberry.field(description="Get a user by email")
    async def getUserByEmail(self, email: str) -> UserType:
        user = db["users"].find_one({"email": email})
        if user:
            user["id"] = str(user.pop("_id"))
            return UserType(**user)
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

    @strawberry.field(
        permission_classes=[IsAuthenticated],
        description="Bring data about the current user",
    )
    async def me(self, info) -> UserType | None:
        token = info.context["request"].headers["Authorization"].split("Bearer ")[-1]
        user = getCurrentUser(token)
        return user

    @strawberry.field(description="Get a list of users.")
    async def getAllUsers(
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
    async def getAllReminders(
        self,
        info,
        order_by: str,
        limit: int,
        offset: int = 0,
        desc: bool = False,
    ) -> PaginationWindow[ReminderType]:
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
    async def getReminderById(self, id: str, info) -> ReminderType:
        token = info.context["request"].headers["Authorization"].split("Bearer ")[-1]
        return await getReminder(id, token)

    @strawberry.field(
        description="Get a list of chats by user", permission_classes=[IsAuthenticated]
    )
    async def getAllChats(
        self,
        info,
        order_by: str,
        limit: int,
        offset: Optional[int] = 0,
        desc: Optional[bool] = False,
    ) -> PaginationWindow[ChatType]:
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
    async def getAllMessages(
        self,
        info,
        order_by: str,
        limit: int,
        chat_id: str,
        offset: Optional[int] = 0,
        desc: Optional[bool] = False,
    ) -> PaginationWindow[MessageType]:
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

    @strawberry.field(description="Get a list of IA models")
    async def getAllIaModels(
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
