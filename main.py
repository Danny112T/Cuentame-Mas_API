import strawberry
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
from strawberry.schema.config import StrawberryConfig
# from src.graphql.schemas.mutation_schema import Mutation
from src.graphql.schemas.query_schema import Query


schema = strawberry.Schema(
    Query, config=StrawberryConfig(auto_camel_case=True)
)

app = FastAPI()
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")
