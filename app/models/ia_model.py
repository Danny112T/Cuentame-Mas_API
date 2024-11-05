import strawberry
from pydantic import BaseModel, Field


class Iamodel(BaseModel):
    id: str = Field(None, alias="id")
    name: str
    algorithm: str
    params: str
    description: str
    path: str

    class Config:
        from_attributes = True


@strawberry.experimental.pydantic.type(model=Iamodel)
class IamodelType:
    id: strawberry.ID
    name: str
    algorithm: str
    params: str
    description: str
    path: str
