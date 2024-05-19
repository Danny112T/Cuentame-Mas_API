import strawberry
from app.graphql.schemas.input_schema import CreateUserInput, loginInput
from app.models.user import UserType, TokenType
from app.graphql.resolvers.users_resolver import createUser, login


@strawberry.type
class Mutation:
    @strawberry.mutation(description="Create a new user")
    async def registerUser(self, input: CreateUserInput) -> UserType:
        return await createUser(input)

    @strawberry.mutation(description="login a user")
    async def loginUser(self, input: loginInput) -> TokenType:
        return await login(input)


