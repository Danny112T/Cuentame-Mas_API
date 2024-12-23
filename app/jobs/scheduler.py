from pip._vendor.requests import delete
import logging
from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_ERROR

from app.core.db import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JobScheduler:
    def __init__(self) -> None:
        self.scheduler = AsyncIOScheduler()
        self.setup_listeners()

    def setup_listeners(self) -> None:
        self.scheduler.add_listener(
            self.job_error_listener,
            EVENT_JOB_ERROR,
        )

    async def job_error_listener(self, event) -> None:
        logger.error(f"Job failed: {event.job_id}")
        logger.error(f"Exception: {event.exception}")

    async def cleanup_guest_sessions(self) -> None:
        try:
            cutoff = datetime.now() - timedelta(days=1)
            result = db["guest_sessions"].delete_many({"created_at": {"$lt": cutoff}})
            logger.info(f"Cleaned up {result.deleted_count} sessions")
        except Exception as e:
            logger.error(f"Error in cleaning job: {str(e)}")
            raise

    def start(self) -> None:
        try:
            self.scheduler.add_job(
                self.cleanup_guest_sessions,
                CronTrigger(hour=0, minute=0),
                id="cleanup_guest_messages",
                replace_existing=True,
            )
            self.scheduler.start()
            logger.info("Scheduler started successfully")
        except Exception as e:
            logger.error(f"Failed to start scheduler: {str(e)}")
            raise
