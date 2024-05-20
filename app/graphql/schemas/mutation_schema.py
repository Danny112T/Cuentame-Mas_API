import strawberry
from app.graphql.schemas.input_schema import (
    CreateUserInput,
    UpdateUserInput,
    loginInput,
)
from app.models.user import UserType, TokenType
from app.graphql.resolvers.users_resolver import createUser, updateUser, deleteUser, login


@strawberry.type
class Mutation:
    @strawberry.mutation(description="Create a new user")
    async def registerUser(self, input: CreateUserInput) -> UserType:
        return await createUser(input)

    @strawberry.mutation(description="Update a user")
    async def updateUser(self, input: UpdateUserInput) -> UserType:
        return await updateUser(input)
    
    @strawberry.mutation(description="delete a user")
    async def deleteUser(self, email: str) -> UserType:
        return await deleteUser(email)
    

    @strawberry.mutation(description="login a user")
    async def loginUser(self, input: loginInput) -> TokenType:
        return await login(input)
