import strawberry
from src.graphql.schemas.input_schema import CreateUserInput, loginInput
from src.graphql.models.user import UserType, loginType
from src.graphql.resolvers.users_resolver import createUser


@strawberry.type
class Mutation:
    @strawberry.mutation(description="Create a new user")
    async def registerUser(self, input: CreateUserInput) -> UserType:
        return await createUser(input)

    @strawberry.mutation(description="login a user")
    async def loginUser(self, input: loginInput) -> loginType:
        return await createUser(input)