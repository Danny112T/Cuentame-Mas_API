import strawberry
from bson import ObjectId
from app.models.user import UserType
from fastapi import HTTPException, status
from app.database.db import db
from app.graphql.types.paginationWindow import PaginationWindow
from app.graphql.resolvers.users_resolver import (
    getCurrentUser,
    get_pagination_window,
)
from app.auth.JWTBearer import IsAuthenticated


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
