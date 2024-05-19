from jose import jwt
from app.database.db import collection_name
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from app.models.user import UserType, TokenType
from app.graphql.schemas.input_schema import CreateUserInput, loginInput
from app.auth.JWTManager import (
    JWTManager,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    SECRET,
)


def makeUserDict(input: CreateUserInput) -> dict:
    return {
        "name": input.name,
        "lastname": input.lastname,
        "email": input.email,
        "created_at": datetime.now(),
        "updated_at": None,
    }


async def createUser(input: CreateUserInput) -> UserType:
    if collection_name.find_one({"email": input.email}) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists"
        )

    user_dict = makeUserDict(input)
    user_dict["password"] = JWTManager.hashPassword(input.password)

    insert_result = collection_name.insert_one(user_dict)
    if insert_result.acknowledged:
        inserted_user = collection_name.find_one({"_id": insert_result.inserted_id})
        if inserted_user:
            inserted_user["id"] = str(inserted_user.pop("_id"))
            return UserType(**inserted_user)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve inserted user",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to insert user",
        )


def getCurrentUser(token: str) -> UserType | None:
    user_info = JWTManager.verify_jwt(token)
    if user_info is not None:
        user = collection_name.find_one({"email": user_info["sub"]})
        user["id"] = str(user.pop("_id"))
        return UserType(**user)
    return None


async def login(input: loginInput) -> TokenType:
    user = collection_name.find_one({"email": input.email})
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User does not exist"
        )
    if not JWTManager.checkPassword(input.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect credentials"
        )

    access_token = {
        "sub": user["email"],
        "exp": datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }

    return TokenType(
        **{
            "access_token": jwt.encode(access_token, SECRET, algorithm=ALGORITHM),
            "token_type": "bearer",
        }
    )
