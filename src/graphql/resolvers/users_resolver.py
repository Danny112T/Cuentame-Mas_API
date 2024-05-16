from datetime import datetime, timedelta
from fastapi import HTTPException, status
from bcrypt import hashpw, gensalt, checkpw
from jose import JWTError, jwt
from os import environ
import typing
from strawberry.types import Info
from strawberry.permission import BasePermission
from src.graphql.config.db.db import collection_name
from src.graphql.models.user import UserType, TokenType
from src.graphql.schemas.input_schema import CreateUserInput, loginInput

ALGORITHM = environ.get("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
    environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "15000")
)
SECRET = environ.get("JWT_SECRET")


def makeUserDict(input: CreateUserInput) -> dict:
    return {
        "name": input.name,
        "lastname": input.lastname,
        "email": input.email,
        "created_at": datetime.now(),
        "updated_at": None,
    }


def hashPassword(password: str) -> str:
    passW = password.encode("utf-8")
    return hashpw(passW, gensalt()).decode("utf-8")


def checkPassword(password: str, hashed: str) -> bool:
    passW = password.encode("utf-8")
    hashed = hashed.encode("utf-8")
    return checkpw(passW, hashed)


async def createUser(input: CreateUserInput) -> UserType:
    if collection_name.find_one({"email": input.email}) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists"
        )

    user_dict = makeUserDict(input)
    user_dict["password"] = hashPassword(input.password)

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
    user_info = verify_jwt(token)
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
    if not checkPassword(input.password, user["password"]):
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


def verify_jwt(token: str):
    try:
        decode_token = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        current_timestamp = datetime.now().timestamp()
        if decode_token is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        elif decode_token["exp"] <= current_timestamp:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credential's token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return decode_token
    except ValueError:
        return False


class IsAuthenticated(BasePermission):
    message = "User is not Authenticated"

    def has_permission(self, source: typing.Any, info: Info, **kwargs) -> bool:
        request = info.context["request"]
        # Access headers authentication
        authentication = request.headers["Authorization"]
        if authentication:
            token = authentication.split("Bearer ")[-1]
            user = getCurrentUser(token)
            if user:
                return True
        return False
