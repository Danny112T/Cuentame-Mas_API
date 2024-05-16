import strawberry
from bson import ObjectId
from fastapi import HTTPException, status
from src.graphql.models.user import UserType
from src.graphql.config.db.db import collection_name
from src.graphql.resolvers.users_resolver import IsAuthenticated, getCurrentUser


@strawberry.type
class Query:
    @strawberry.field(description=" Print Hello World Just For meh")
    async def helloWorld(self) -> str:
        return "HelloWorld"

    @strawberry.field(description="Get a user by id")
    async def getUserbyId(self, id: str) -> UserType:
        user = collection_name.find_one({"_id": ObjectId(id)})
        if user:
            user["id"] = str(user.pop("_id"))
            return UserType(**user)
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
            )

    @strawberry.field(description="Get a user by email")
    async def getUserByEmail(self, email: str) -> UserType:
        user = collection_name.find_one({"email": email})
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
