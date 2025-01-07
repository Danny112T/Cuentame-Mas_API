import asyncio
import logging
from datetime import datetime, timedelta

from apscheduler.events import EVENT_JOB_ERROR, EVENT_SCHEDULER_SHUTDOWN
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.db import db
from app.jobs.reminder_job import check_reminders

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JobScheduler:
    def __init__(self) -> None:
        self.scheduler = AsyncIOScheduler()
        self.setup_listeners()
        self._shutdown_event = asyncio.Event()

    def setup_listeners(self) -> None:
        self.scheduler.add_listener(
            self.job_error_listener,
            EVENT_JOB_ERROR,
        )
        self.scheduler.add_listener(
            self.shutdown_listener,
            EVENT_SCHEDULER_SHUTDOWN,
        )

    async def job_error_listener(self, event) -> None:
        logger.error(f"Job failed: {event.job_id}")
        logger.error(f"Exception: {event.exception}")

    async def shutdown_listener(self, event) -> None:
        logger.info("Scheduler shutdown event received")
        self._shutdown_event.set()

    async def cleanup_guest_sessions(self) -> None:
        try:
            cutoff = datetime.now() - timedelta(days=1)
            expired_sessions = db["guest_sessions"].find({"created_at": {"$lt": cutoff}, "status": "ACTIVE"})

            for session in expired_sessions:
                session_id = session["session_id"]
                db["guest_sessions"].update_one(
                    {"session_id": session_id},
                    {"$set": {"status": "EXPIRED"}}
                )

                db["chats"].update_one(
                    {"session_id": session_id},
                    {"$set": {"expired": "EXPIRED"}}
                )

            logger.info(f"Cleaned up expired guest sessions")
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

            self.scheduler.add_job(
                check_reminders,
                'interval',
                minutes=1,
                id="check_reminders",
                replace_existing=True,
            )

            self.scheduler.start()
            logger.info("Scheduler started successfully")
        except Exception as e:
            logger.error(f"Failed to start scheduler: {str(e)}")
            raise

    async def shutdown(self, wait: bool = True) -> None:
        """
        Realiza un apagado controlado del scheduler.

        Args:
            wait (bool): Si es True, espera a que todos los jobs en ejecución terminen.
        """
        try:
            logger.info("Initiating scheduler shutdown...")
            self.scheduler.pause()

            if wait:
                running_jobs = self.scheduler.get_jobs()
                if running_jobs:
                    logger.info(f"Waiting for {len(running_jobs)} jobs to complete...")
                    await asyncio.gather(*(job.remove() for job in running_jobs))

            self.scheduler.shutdown(wait=False)
            await self._shutdown_event.wait()
            logger.info("Scheduler shutdown completed successfully")
        except Exception as e:
            logger.exception(f"Error during scheduler shutdown: {str(e)}")
            raise
        finally:
            self.scheduler = None
            self._shutdown_event.clear()

    @property
    def is_running(self) -> bool:
        """Verifica si el scheduler está activo."""
        return self.scheduler and self.scheduler.running

    async def get_running_jobs(self) -> list:
        """Obtiene la lista de jobs en ejecución."""
        try:
            return self.scheduler.get_jobs() if self.is_running else []
        except Exception as e:
            logger.exception(f"Error getting running jobs: {str(e)}")
            raise
