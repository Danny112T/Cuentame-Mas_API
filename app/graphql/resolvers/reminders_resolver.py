from datetime import datetime
from pymongo import DESCENDING, ASCENDING
from app.graphql.schemas.input_schema import CreateReminderInput, UpdateReminderInput
from app.models.reminder import ReminderType
from app.auth.JWTManager import JWTManager
from fastapi import HTTPException, status
from app.database.db import db
from bson import ObjectId
from app.graphql.types.paginationWindow import PaginationWindow


def makeReminderDict(input: CreateReminderInput) -> dict:
    return {
        "title": input.title,
        "description": input.description,
        "finishDate": input.finishDate,
        "created_at": datetime.now(),
        "updated_at": None,
    }


def makeUpdateReminderDict(input: UpdateReminderInput) -> dict:
    return {
        "title": input.title,
        "description": input.description,
        "finishDate": input.finishDate,
        "updated_at": datetime.now(),
    }


async def createReminder(input: CreateReminderInput, token: str) -> ReminderType:
    user_info = JWTManager.verify_jwt(token)
    if user_info is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    reminder_dict = makeReminderDict(input)

    reminder_dict["user_id"] = user_info["sub"]

    reminder = db["reminders"].insert_one(reminder_dict)
    if reminder.acknowledged:
        reminder = db["reminders"].find_one({"_id": reminder.inserted_id})
        if reminder:
            update_result = db["users"].update_one(
                {"_id": ObjectId(user_info["sub"])},
                {"$push": {"reminders": str(reminder["_id"])}},
            )
            if update_result.modified_count == 0:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update user with reminder",
                )
            reminder["id"] = str(reminder.pop("_id"))
            return ReminderType(**reminder)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve inserted reminder",
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to insert reminder",
        )


async def get_reminders_pagination_window(
    token: str,
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

    user_info = JWTManager.verify_jwt(token)
    if user_info is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    data = []
    order_type = ASCENDING

    if limit <= 0 or limit > 100:
        raise Exception(f"limit ({limit}) must be between 0-100")

    if desc:
        order_type = DESCENDING
    else:
        order_type = ASCENDING

    for x in db[dataset].find({"user_id": user_info["sub"]}).sort(order_by, order_type):
        x["id"] = str(x.pop("_id"))
        data.append(ItemType(**x))

    total_items_count = db[dataset].count_documents({"user_id": user_info["sub"]})

    if offset != 0 and not 0 <= offset < db[dataset].count_documents({}):
        raise Exception(
            f"offset ({offset}) is out of range " f"(0-{total_items_count - 1})"
        )

    data = data[offset : offset + limit]

    return PaginationWindow(items=data, total_items_count=total_items_count)


async def getReminder(id: str, token: str) -> ReminderType:
    user_info = JWTManager.verify_jwt(token)
    if user_info is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    reminder = db["reminders"].find_one({"_id": ObjectId(id)})
    if reminder is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found",
        )

    if reminder["user_id"] != user_info["sub"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to see this reminder",
        )
    reminder["id"] = str(reminder.pop("_id"))
    return ReminderType(**reminder)


async def updateReminder(input: UpdateReminderInput, token: str) -> ReminderType:
    user_info = JWTManager.verify_jwt(token)
    if user_info is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    reminder = db["reminders"].find_one({"_id": ObjectId(input.id)})
    if reminder is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found",
        )

    if reminder["user_id"] != user_info["sub"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update this reminder",
        )

    reminder_dict = makeUpdateReminderDict(input)
    if reminder_dict["title"] is None:
        reminder_dict["title"] = reminder["title"]

    if reminder_dict["description"] is None:
        reminder_dict["description"] = reminder["description"]

    if reminder_dict["finishDate"] is None:
        reminder_dict["finishDate"] = reminder["finishDate"]

    update_result = db["reminders"].update_one(
        {"_id": ObjectId(reminder["_id"])},
        {"$set": reminder_dict},
        upsert=False,
    )

    if update_result.matched_count == 1:
        updated_reminder = db["reminders"].find_one({"_id": ObjectId(input.id)})
        updated_reminder["id"] = str(updated_reminder.pop("_id"))
        return ReminderType(**updated_reminder)
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update reminder",
        )


async def deleteReminder(id: str, token: str) -> ReminderType:
    user_info = JWTManager.verify_jwt(token)
    if user_info is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    reminder = db["reminders"].find_one({"_id": ObjectId(id)})
    if reminder is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found",
        )

    if reminder["user_id"] != user_info["sub"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to delete this reminder",
        )

    db["reminders"].delete_one({"_id": ObjectId(id)})
    reminder["id"] = str(reminder.pop("_id"))
    return ReminderType(**reminder)
