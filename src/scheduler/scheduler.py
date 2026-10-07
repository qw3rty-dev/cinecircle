from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from .jobs import cleanup_expired_job, genre_sync_job

scheduler = AsyncIOScheduler()


def configure_scheduler():
    scheduler.add_job(
        genre_sync_job,
        trigger=IntervalTrigger(days=7),
        id="genre-sync",
        replace_existing=True,
    )
    scheduler.add_job(
        cleanup_expired_job,
        trigger=IntervalTrigger(hours=24),
        id="cleanup",
        replace_existing=True,
    )
