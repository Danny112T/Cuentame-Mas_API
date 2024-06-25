import strawberry
from app.graphql.schemas.input_schema import (
    CreateUserInput,
    UpdateUserInput,
    loginInput,
)
from app.models.user import UserType, TokenType
from app.graphql.resolvers.users_resolver import createUser, updateUser, deleteUser, login
from app.auth.JWTBearer import IsAuthenticated
from fastapi import HTTPException, status

@strawberry.type
class Mutation:
    @strawberry.mutation(description="Create a new user")
    async def registerUser(self, input: CreateUserInput) -> UserType:
        return await createUser(input)

    @strawberry.mutation(
        description="Update a user",
        permission_classes=[IsAuthenticated]
    )
    async def updateUser(self, input: UpdateUserInput, info) -> UserType:
        if "Authorization" not in info.context["request"].headers:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is not authenticated")
        
        if info.context["request"].headers["Authorization"].split("Bearer ")[-1] is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is not authenticated")

        token = info.context["request"].headers["Authorization"].split("Bearer ")[-1]
        return await updateUser(input, token)
    
    @strawberry.mutation(
        description="delete a user",
        permission_classes=[IsAuthenticated]   
    )
    async def deleteUser(self, email: str, info) -> UserType:
        if "Authorization" not in info.context["request"].headers:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is not authenticated")
        
        if info.context["request"].headers["Authorization"].split("Bearer ")[-1] is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User is not authenticated")

        token = info.context["request"].headers["Authorization"].split("Bearer ")[-1]
        return await deleteUser(email, token)
    

    @strawberry.mutation(description="login a user")
    async def loginUser(self, input: loginInput) -> TokenType:
        return await login(input)
