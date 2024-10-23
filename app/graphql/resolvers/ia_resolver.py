from bson.objectid import ObjectId
from fastapi import HTTPException, status
from mlx_lm.utils import generate, load
from pymongo import ASCENDING, DESCENDING

from app.auth.JWTManager import JWTManager
from app.core.db import db
from app.graphql.schemas.input_schema import RegisterIaModelInput
from app.graphql.types.paginationWindow import PaginationWindow
from app.models.ia_model import IamodelType


def make_ia_model_dict(input: RegisterIaModelInput) -> dict:
    return {
        "name": input.name,
        "algorithm": input.algorithm,
        "params": input.params,
        "description": input.description,
        "path": input.path,
    }


# Register Model
async def register_ia_model(input: RegisterIaModelInput, token) -> IamodelType:
    user_info = JWTManager.verify_jwt(token)
    if user_info is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    model_dict = make_ia_model_dict(input)
    model = db["models"].insert_one(model_dict)
    if model.acknowledged:
        inserted_model = db["models"].find_one({"_id": model.inserted_id})
        if inserted_model:
            inserted_model["id"] = str(inserted_model.pop("_id"))
            return IamodelType(**inserted_model)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve inserted model",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to insert model",
        )

# Get Model


# Update Model


# Delete Model


# Get all models
async def get_models_pagination_window(
    dataset: str,
    ItemType: type,
    order_by: str,
    limit: int,
    offset: int = 0,
    desc: bool = False,
) -> PaginationWindow:
    """
    Get one pagination window on the given dataset for the given limit
    and offset, ordered by the given attribute and filtered using the
    given filters
    """
    data = []
    order_type = ASCENDING
    if limit <= 0 or limit > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"limit ({limit}) must be between 0-100",
        )

    if order_by is None:
        order_by = "name"

    order_type = DESCENDING if desc else ASCENDING
    for x in db[dataset].find().sort(order_by, order_type):
        x["id"] = str(x.pop("_id"))
        data.append(ItemType(**x))

    total_items_count = db[dataset].count_documents({})
    if offset != 0 and not 0 <= offset <= total_items_count:
        raise Exception(
            f"offset ({offset}) is out of range" f"(0-{total_items_count -1 })"
        )

    return PaginationWindow(items=data, total_items_count=total_items_count)


# Generate response
def generate_response(
    content: str, chat_id: str, model_id: str, max_length: int = 512
) -> tuple[str, str]:
    if model_id is None:
        model_id = "66f37d8bb38ac24ead72721e"

    db_ia_model = db["models"].find_one({"_id": ObjectId(model_id)})
    if db_ia_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model not found",
        )

    path = db_ia_model.get("path")
    model, tokenizer = load(path)

    conversation = list(
        db["messages"].find({"chat_id": chat_id}).sort("created_at", DESCENDING)
    )
    messages = []
    if len(conversation) == 0:
        messages.append({"role": "user", "content": content})
    else:
        for message in conversation:
            messages.append({"role": message["role"], "content": message["content"]})
        messages.append({"role": "user", "content": content})

    prompt = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )

    return generate(model, tokenizer, prompt, max_tokens=max_length)
