from datetime import datetime, timedelta
from re import fullmatch

from bson import ObjectId
from email_validator import EmailNotValidError, validate_email
from fastapi import HTTPException, status
from jose import jwt
from pymongo import ASCENDING, DESCENDING

from app.auth.JWTManager import JWTManager
from app.core.config import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    ALGORITHM,
    EMAIL_VAL,
    JWT_SECRET,
)
from app.core.db import db
from app.graphql.schemas.input_schema import (
    CreateUserInput,
    UpdateUserInput,
    loginInput,
)
from app.graphql.types.paginationWindow import PaginationWindow
from app.models.chat import ChatType
from app.models.message import MessageType
from app.models.reminder import ReminderType
from app.models.user import (
    REGIMEN_FISCAL_DESCRIPTIONS,
    RegimenFiscal,
    TokenType,
    UserType,
)

REGEX = r"(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[#$@!%&*?_])(?!\s)[a-zA-Z\d#$@!%&*?_]{6,}$"

def get_regimen_fiscal_description(regimen: RegimenFiscal) -> str:
    return REGIMEN_FISCAL_DESCRIPTIONS[regimen]

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


async def create_user(input: CreateUserInput) -> UserType:
    if db["users"].find_one({"email": input.email}) is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario ya existe"
        )

    try:
        email_info = validate_email(input.email, check_deliverability=EMAIL_VAL)
    except EmailNotValidError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e)

    if not fullmatch(REGEX, input.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña debe contener al menos una letra minúscula, una mayúscula, un dígito, un carácter especial y debe tener al menos 6 caracteres",
        )

    user_dict = makeCreateUserDict(input)
    user_dict["email"] = email_info.normalized
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
                detail="Error al recuperar el usuario",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al crear el usuario",
        )


async def update_user(input: UpdateUserInput, token: str) -> UserType:
    user_info = JWTManager.verify_jwt(token)
    if user_info is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db["users"].find_one({"_id": ObjectId(user_info["sub"])})
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario no existe"
        )

    user_dict = makeUpdateUserDict(input)
    if (input.old_password is not None) & (input.new_password is None):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña antigua debe ser acompañada por la nueva contraseña",
        )
    if input.new_password is not None:
        if input.old_password is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La nueva contraseña debe ser acompañada por la antigua contraseña",
            )
        if not JWTManager.checkPassword(input.old_password, user["password"]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Credenciales inválidas"
            )
        if not fullmatch(REGEX, input.new_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="La contraseña debe contener al menos una letra minúscula, una mayúscula, un dígito, un carácter especial y debe tener al menos 6 caracteres",
            )
        user_dict["password"] = JWTManager.hashPassword(input.new_password)

    if user_dict["name"] is None:
        user_dict["name"] = user["name"]

    if user_dict["lastname"] is None:
        user_dict["lastname"] = user["lastname"]

    if user_dict["email"] is None:
        user_dict["email"] = user["email"]

    if user_dict["regimenFiscal"] is None:
        user_dict["regimenFiscal"] = user["regimenFiscal"]

    elif isinstance(user_dict["regimenFiscal"], RegimenFiscal):
            user_dict["regimenFiscal"] = get_regimen_fiscal_description(user_dict["regimenFiscal"])

    update_result = db["users"].update_one(
        {"_id": ObjectId(user["_id"])}, {"$set": user_dict}, upsert=False
    )

    if update_result.matched_count == 1:
        updated_user = db["users"].find_one({"email": user["email"]})
        updated_user["id"] = str(updated_user.pop("_id"))
    return UserType(**updated_user)


async def delete_user(email: str, token: str) -> UserType:
    user_info = JWTManager.verify_jwt(token)
    if user_info is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db["users"].find_one({"_id": ObjectId(user_info["sub"])})
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario no existe"
        )

    if user["email"] != email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="El correo electrónico no coincide"
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
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El limite ({limit}) debe estar entre 0-100",
        )

    if order_by is None:
        order_by = "created_at"

    order_type = DESCENDING if desc else ASCENDING

    for x in db[dataset].find().sort(order_by, order_type):
        x["id"] = str(x.pop("_id"))
        user_reminders = db["reminders"].find({"user_id": str(x["id"])})
        reminders = []
        chats = []
        for reminder in user_reminders:
            reminder["id"] = str(reminder.pop("_id"))
            reminders.append(reminder)

        for chat in db["chats"].find({"user_id": str(x["id"])}):
            chat["id"] = str(chat.pop("_id"))
            chats.append(chat)

        x["reminders"] = [ReminderType(**reminder) for reminder in reminders]
        x["chats"] = [ChatType(**chat) for chat in chats]
        data.append(ItemType(**x))

    total_items_count = db[dataset].count_documents({})

    if offset != 0 and not 0 <= offset < db[dataset].count_documents({}):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"El offset ({offset}) esta fuera de rango (0-{total_items_count -1 })",
        )

    data = data[offset : offset + limit]

    return PaginationWindow(items=data, total_items_count=total_items_count)


def getCurrentUser(token: str) -> UserType | None:
    user_info = JWTManager.verify_jwt(token)
    if user_info is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db["users"].find_one({"_id": ObjectId(user_info["sub"])})
    user["id"] = str(user.pop("_id"))
    user_reminders = db["reminders"].find({"user_id": str(user["id"])})
    reminders = []
    chats = []
    for reminder in user_reminders:
        reminder["id"] = str(reminder.pop("_id"))
        reminders.append(reminder)

    for chat in db["chats"].find({"user_id": str(user["id"])}):
        chat["id"] = str(chat.pop("_id"))
        chats.append(chat)

    for x in chats:
        messages = []
        for message in (
            db["messages"].find({"chat_id": x["id"]}).sort("created_at", ASCENDING)
        ):
            message["id"] = str(message.pop("_id"))
            messages.append(message)
        x["messages"] = [MessageType(**message) for message in messages]

    user["reminders"] = [ReminderType(**reminder) for reminder in reminders]
    user["chats"] = [ChatType(**chat) for chat in chats]

    return UserType(**user)


async def login(input: loginInput) -> TokenType:
    user = db["users"].find_one({"email": input.email})
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario no existe"
        )
    if not JWTManager.checkPassword(input.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Credenciales inválidas"
        )

    access_token = {
        "sub": str(user["_id"]),
        "exp": datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    }

    return TokenType(
        **{
            "access_token": jwt.encode(access_token, JWT_SECRET, algorithm=ALGORITHM),
            "token_type": "bearer",
        }
    )
