import strawberry
from fastapi import HTTPException, status

import app.graphql.resolvers.chats_resolver as cht
import app.graphql.resolvers.guest_resolver as gs
import app.graphql.resolvers.ia_resolver as ia
import app.graphql.resolvers.messages_resolver as msj
import app.graphql.resolvers.reminders_resolver as remind
import app.graphql.resolvers.users_resolver as usr
import app.graphql.schemas.input_schema as ins
from app.auth.JWTBearer import IsAuthenticated
from app.models.chat import ChatType
from app.models.guest_session import GuestSessionType
from app.models.ia_model import IamodelType
from app.models.message import MessageType
from app.models.reminder import ReminderType
from app.models.user import TokenType, UserType


@strawberry.type
class Mutation:
    """
    Users mutations
    """

    @strawberry.mutation(description="Create a new user")
    async def register_user(self, input: ins.CreateUserInput) -> UserType:
        return await usr.create_user(input)

    @strawberry.mutation(
        description="Update a user", permission_classes=[IsAuthenticated]
    )
    async def update_user(self, input: ins.UpdateUserInput, info) -> UserType:
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
        return await usr.update_user(input, token)

    @strawberry.mutation(
        description="delete a user", permission_classes=[IsAuthenticated]
    )
    async def delete_user(self, email: str, info) -> UserType:
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
        return await usr.delete_user(email, token)

    @strawberry.mutation(description="login a user")
    async def login_user(self, input: ins.loginInput) -> TokenType:
        return await usr.login(input)

    """
    Reminders mutations
    """

    @strawberry.mutation(
        description="Create a reminder", permission_classes=[IsAuthenticated]
    )
    async def create_reminder(self, input: ins.CreateReminderInput, info) -> ReminderType:
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
        return await remind.create_reminder(input, token)

    @strawberry.mutation(
        description="Update a reminder", permission_classes=[IsAuthenticated]
    )
    async def update_reminder(self, input: ins.UpdateReminderInput, info) -> ReminderType:
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
        return await remind.update_reminder(input, token)

    @strawberry.mutation(
        description="Delete a reminder", permission_classes=[IsAuthenticated]
    )
    async def delete_reminder(self, id: str, info) -> ReminderType:
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
        return await remind.delete_reminder(id, token)

    """
    Chats mutations
    """

    @strawberry.mutation(
        description="Create a chat", permission_classes=[IsAuthenticated]
    )
    async def create_chat(self, input: ins.CreateChatInput, info) -> ChatType:
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
        return await cht.create_chat(input, token)

    @strawberry.mutation(
        description="Update a chat", permission_classes=[IsAuthenticated]
    )
    async def update_chat(self, input: ins.UpdateChatInput, info) -> ChatType:
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
        return await cht.update_chat(input, token)

    @strawberry.mutation(
        description="Delete a chat", permission_classes=[IsAuthenticated]
    )
    async def delete_chat(self, id: str, info) -> ChatType:
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
        return await cht.delete_chat(id, token)

    """
    Messages mutations
    """

    @strawberry.mutation(
        description="Create a message from a Authenticated user",
        permission_classes=[IsAuthenticated],
    )
    async def create_message(
        self, input: msj.CreateMessageInput, info
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
        return await msj.create_message(input, token)

    @strawberry.mutation(
        description="Update a message from an Authenticated user ",
        permission_classes=[IsAuthenticated],
    )
    async def update_message_data(
        self, input: ins.UpdateMessageInput, info
    ) -> MessageType | None:
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
        return await msj.update_message(input, token)

    @strawberry.mutation(
        description="Update a content of a message from an Authenticated user ",
        permission_classes=[IsAuthenticated],
    )
    async def update_message_content(
        self, input: ins.RegenerateMessageInput, info
    ) -> tuple[MessageType, MessageType] | None:
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
        return await msj.regenerate_message(input, token)

    @strawberry.mutation(
        description="Delete a message from an Authenticated user ",
        permission_classes=[IsAuthenticated],
    )
    async def delete_message(
        self, input: ins.DeleteMessageInput, info
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
        return await msj.delete_message(input, token)

    """
    IA models mutations
    """

    @strawberry.mutation(
        description="Register a new IA model chat into the sistem",
        permission_classes=[IsAuthenticated],
    )
    async def register_ia_model(self, input: ins.RegisterIaModelInput, info) -> IamodelType:
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
        return await ia.register_ia_model(input, token)

    @strawberry.mutation(
        description="Update a IA model chat into the sistem",
        permission_classes=[IsAuthenticated],
    )
    async def update_ia_model(self, input: ins.UpdateIaModelInput, info) -> IamodelType:
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
        return await ia.update_ia_model(input, token)

    @strawberry.mutation(
        description="Delete a IA model chat into the sistem",
        permission_classes=[IsAuthenticated],
    )
    async def delete_ia_model(self, input: ins.DeleteIaModelInput, info) -> IamodelType:
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
        return await ia.delete_ia_model(input, token)


    """
    Guest mutations
    """
    @strawberry.mutation(description="Create a guest session")
    async def create_guest_session(self) -> GuestSessionType:
        return await gs.create_guest_session()

    @strawberry.mutation(description="Create message from a guest session")
    async def create_guest_message(self, input: ins.CreateGuestMessageInput) -> tuple[MessageType, MessageType]:
        return await msj.create_guest_message(input)
