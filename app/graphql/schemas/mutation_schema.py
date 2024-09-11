import strawberry
from app.models.chat import ChatType
from fastapi import HTTPException, status
from app.models.message import MessageType
from app.models.reminder import ReminderType
from app.auth.JWTBearer import IsAuthenticated
from app.models.user import UserType, TokenType
from app.graphql.schemas.input_schema import *
from app.graphql.resolvers.users_resolver import *
from app.graphql.resolvers.reminders_resolver import *
from app.graphql.resolvers.chats_resolver import *
from app.graphql.resolvers.messages_resolver import *


@strawberry.type
class Mutation:
    @strawberry.mutation(description="Create a new user")
    async def registerUser(self, input: CreateUserInput) -> UserType:
        return await createUser(input)

    @strawberry.mutation(
        description="Update a user", permission_classes=[IsAuthenticated]
    )
    async def updateUser(self, input: UpdateUserInput, info) -> UserType:
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
        return await updateUser(input, token)

    @strawberry.mutation(
        description="delete a user", permission_classes=[IsAuthenticated]
    )
    async def deleteUser(self, email: str, info) -> UserType:
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
        return await deleteUser(email, token)

    @strawberry.mutation(description="login a user")
    async def loginUser(self, input: loginInput) -> TokenType:
        return await login(input)

    @strawberry.mutation(
        description="Create a reminder", permission_classes=[IsAuthenticated]
    )
    async def createReminder(self, input: CreateReminderInput, info) -> ReminderType:
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
        return await createReminder(input, token)

    @strawberry.mutation(
        description="Update a reminder", permission_classes=[IsAuthenticated]
    )
    async def updateReminder(self, input: UpdateReminderInput, info) -> ReminderType:
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
        return await updateReminder(input, token)

    @strawberry.mutation(
        description="Delete a reminder", permission_classes=[IsAuthenticated]
    )
    async def deleteReminder(self, id: str, info) -> ReminderType:
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
        return await deleteReminder(id, token)

    @strawberry.mutation(
        description="Create a chat", permission_classes=[IsAuthenticated]
    )
    async def createChat(self, input: CreateChatInput, info) -> ChatType:
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
        return await createChat(input, token)

    @strawberry.mutation(
        description="Update a chat", permission_classes=[IsAuthenticated]
    )
    async def updateChat(self, input: UpdateChatInput, info) -> ChatType:
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
        return await updateChat(input, token)

    @strawberry.mutation(
        description="Delete a chat", permission_classes=[IsAuthenticated]
    )
    async def deleteChat(self, id: str, info) -> ChatType:
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
        return await deleteChat(id, token)

    @strawberry.mutation(
        description="Create a message from a Authenticated user",
        permission_classes=[IsAuthenticated],
    )
    async def createMessage(
        self, input: CreateMessageInput, info
    ) -> tuple[MessageType, MessageType]:
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
        return await createMessage(input, token)
