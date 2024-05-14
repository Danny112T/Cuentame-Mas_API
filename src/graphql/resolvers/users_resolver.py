from datetime import datetime
from fastapi import HTTPException, status
from bcrypt import hashpw, gensalt, checkpw
from jose import JWTError, jwt
from src.graphql.models.user import UserType, TokenType
from src.graphql.config.db.db import collection_name
from src.graphql.schemas.input_schema import CreateUserInput
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15000

oauth2 = OAuth2PasswordBearer(tokenUrl="login")


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


async def loginUser(input: loginInput) -> TokenType:
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
        "sub": jwt.encode(access_token, SECRET, algorithm=ALGORITHM),
        "exp": datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }
