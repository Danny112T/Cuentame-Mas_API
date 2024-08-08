from jose import jwt
from pymongo import DESCENDING, ASCENDING
from datetime import datetime, timedelta
from bson import ObjectId
from fastapi import HTTPException, status
from re import fullmatch
from app.database.db import db
from app.models.user import UserType, TokenType, RegimenFiscal
from app.graphql.types.paginationWindow import PaginationWindow
from app.models.reminder import ReminderType
from app.graphql.schemas.input_schema import (
    CreateUserInput,
    UpdateUserInput,
    loginInput,
)
from app.auth.JWTManager import (
    JWTManager,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    SECRET,
)


REGEX = r"(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[#$@!%&*?_])(?!\s)[a-zA-Z\d#$@!%&*?_]{6,}$"


def makeCreateUserDict(input: CreateUserInput) -> dict:
    return {
        "name": input.name,
        "lastname": input.lastname,
        "email": input.email,
        "created_at": datetime.now(),
        "updated_at": None,
    }


def makeUpdateUserDict(input: UpdateUserInput) -> dict:
    return {
        "name": input.name,
        "lastname": input.lastname,
        "email": input.email,
        "regimenFiscal": input.regimenFiscal,
        "updated_at": datetime.now(),
    }


async def createUser(input: CreateUserInput) -> UserType:
    if db["users"].find_one({"email": input.email}) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists"
        )

    if not fullmatch(REGEX, input.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password must contain at least one lowercase letter, one uppercase letter, one digit, one special character and must be at least 6 characters long",
        )

    user_dict = makeCreateUserDict(input)

    user_dict["password"] = JWTManager.hashPassword(input.password)
    user_dict["regimenFiscal"] = RegimenFiscal.NO_DEFINIDO.value
    user_dict["reminders"] = []

    insert_result = db["users"].insert_one(user_dict)
    if insert_result.acknowledged:
        inserted_user = db["users"].find_one({"_id": insert_result.inserted_id})
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


async def updateUser(input: UpdateUserInput, token: str) -> UserType:
    user_info = JWTManager.verify_jwt(token)
    if user_info is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db["users"].find_one({"_id": ObjectId(user_info["sub"])})
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User does not exist"
        )

    user_dict = makeUpdateUserDict(input)
    if input.password:
        if not fullmatch(REGEX, input.password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password must contain at least one lowercase letter, one uppercase letter, one digit, one special character and must be at least 6 characters long",
            )
        user_dict["password"] = JWTManager.hashPassword(input.password)

    if user_dict["name"] is None:
        user_dict["name"] = user["name"]

    if user_dict["lastname"] is None:
        user_dict["lastname"] = user["lastname"]

    if user_dict["email"] is None:
        user_dict["email"] = user["email"]

    if user_dict["regimenFiscal"] is None:
        user_dict["regimenFiscal"] = user["regimenFiscal"]

    update_result = db["users"].update_one(
        {"_id": ObjectId(user["_id"])}, {"$set": user_dict}, upsert=False
    )

    if update_result.matched_count == 1:
        updated_user = db["users"].find_one({"email": user["email"]})
        updated_user["id"] = str(updated_user.pop("_id"))
    return UserType(**updated_user)


async def deleteUser(email: str, token: str) -> UserType:
    user_info = JWTManager.verify_jwt(token)
    if user_info is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db["users"].find_one({"_id": ObjectId(user_info["sub"])})
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User does not exist"
        )

    if user["email"] != email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email does not match"
        )

    user["id"] = str(user.pop("_id"))
    # TODO: db["users"].update_one({"_id": ObjectId(user["id"])}, {"$set": {"deleted_at": datetime.now()}})
    db["users"].delete_one({"email": email})
    return UserType(**user)


async def get_pagination_window(
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
        raise Exception(f"limit ({limit}) must be between 0-100")

    if desc:
        order_type = DESCENDING
    else:
        order_type = ASCENDING

    for x in db[dataset].find().sort(order_by, order_type):
        x["id"] = str(x.pop("_id"))
        data.append(ItemType(**x))

    total_items_count = db[dataset].count_documents({})

    if offset != 0 and not 0 <= offset < db[dataset].count_documents({}):
        raise Exception(
            f"offset ({offset}) is out of range " f"(0-{total_items_count - 1})"
        )

    data = data[offset : offset + limit]

    return PaginationWindow(items=data, total_items_count=total_items_count)


def getCurrentUser(token: str) -> UserType | None:
    user_info = JWTManager.verify_jwt(token)
    if user_info is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db["users"].find_one({"_id": ObjectId(user_info["sub"])})
    user["id"] = str(user.pop("_id"))
    user_reminders = db["reminders"].find({"user_id": str(user["id"])})
    reminders = []
    for reminder in user_reminders:
        reminder["id"] = str(reminder.pop("_id"))
        reminders.append(reminder)

    user["reminders"] = [ReminderType(**reminder) for reminder in reminders]

    return UserType(**user)


async def login(input: loginInput) -> TokenType:
    user = db["users"].find_one({"email": input.email})
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="User does not exist"
        )
    if not JWTManager.checkPassword(input.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect credentials"
        )

    access_token = {
        "sub": str(user["_id"]),
        "exp": datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }

    return TokenType(
        **{
            "access_token": jwt.encode(access_token, SECRET, algorithm=ALGORITHM),
            "token_type": "bearer",
        }
    )
