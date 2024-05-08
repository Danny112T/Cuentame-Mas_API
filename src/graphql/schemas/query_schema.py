import strawberry


@strawberry.type
class Query:
    @strawberry.field(description=" Print Hello World Just For meh")
    async def helloWorld(self) -> str:
        return "HelloWorld"
