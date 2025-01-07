import logging
from datetime import datetime, timedelta

from bson import ObjectId

from app.core.db import db
from app.models.reminder import Reminder
from app.models.user import User
from app.services.email_service import EmailService

logger = logging.getLogger(__name__)

async def check_reminders():
    try:
        email_service = EmailService()
        now = datetime.now()
        upcoming_reminders = db["reminders"].find({"finishDate": {"$gte": now, "$lt": now + timedelta(hours=1)}})

        for reminder_doc in upcoming_reminders:
            reminder_doc["_id"] = str(reminder_doc.pop("_id"))
            reminder = Reminder(**reminder_doc)
            user_doc = db["users"].find_one({"_id": ObjectId(reminder.user_id)})
            if user_doc is not None:
                user_doc["_id"] = str(user_doc.pop("_id"))
                user = User(**user_doc)
                await email_service.send_reminder_email(user, reminder)
                db["reminders"].update_one(
                                    {"_id": ObjectId(reminder.id)},
                                    {"$set": {"notification_sent": True}}
                                )
                logger.info(f"Sent reminder email to {user.email} for reminder {reminder.title}")

    except Exception as e:
        logger.error(f"Error in check_reminders: {str(e)}")
        raise
