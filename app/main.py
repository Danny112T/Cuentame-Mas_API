import strawberry
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
from strawberry.schema.config import StrawberryConfig

from app.graphql.schemas.mutation_schema import Mutation
from app.graphql.schemas.query_schema import Query
from app.jobs.scheduler import JobScheduler

load_dotenv()
schema = strawberry.Schema(
    query=Query, mutation=Mutation, config=StrawberryConfig(auto_camel_case=True)
)

app = FastAPI()
scheduler = JobScheduler()

@app.on_event("startup")
async def start_scheduler() -> None:
    try:
        scheduler.start()
    except Exception as e:
        print(f"Failed to start scheduler: {e}")

@app.on_event("shutdown")
async def shutdown_scheduler() -> None:
    if scheduler.is_running:
        try:
            await scheduler.shutdown(wait=True)
        except Exception as e:
            print(f"Failed to shutdown scheduler: {e}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/graphql")
