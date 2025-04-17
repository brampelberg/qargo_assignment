from datetime import datetime
import logging
from typing import Any, Dict
from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from dotenv import load_dotenv
from synchronisation_service import SynchronisationService
from utils.logging_config import setup_logging
from utils.utils import get_env_var
from pytz import utc

load_dotenv()

_LOG_LEVEL = get_env_var("LOG_LEVEL")
_LOG_FILE = get_env_var("LOG_FILE")
_LOG_TO_FILE = get_env_var("LOG_TO_FILE").lower() == "true"
_LOG_TO_CONSOLE = get_env_var("LOG_TO_CONSOLE").lower() == "true"

setup_logging(
    log_level=getattr(logging, _LOG_LEVEL, logging.INFO), 
    log_file=_LOG_FILE, 
    log_to_file=_LOG_TO_FILE, 
    log_to_console=_LOG_TO_CONSOLE
)

logger = logging.getLogger(__name__)

def run_sync_job():
    START_YEAR = get_env_var("START_YEAR")
    logger.info("Scheduler triggered synchronization job...")
    try:
        start_time_filter = datetime(year=int(START_YEAR), month=1, day=1)
        sync_service = SynchronisationService(start_time=start_time_filter)
        sync_service.synchronize_unavailabilities()
        logger.info("Synchronization job completed successfully.")
    except Exception as e:
        logger.exception(f"An error occurred during the scheduled sync job: {e}")

if __name__ == "__main__":
    SYNC_CRON_SCHEDULE = get_env_var("SYNC_CRON_SCHEDULE")
    logger.info("=============================================")
    logger.info(" Starting APScheduler for Qargo Sync Service ")
    logger.info(f" Schedule: CRON '{SYNC_CRON_SCHEDULE}'")
    logger.info("=============================================")

    jobstores = {
        'default': MemoryJobStore()
    }

    executors = {
        'default': ThreadPoolExecutor(max_workers=1)
    }

    job_defaults: Dict[str, Any] = {
        'coalesce': True,
        'max_instances': 1,
        'misfire_grace_time': 5*60
    }

    scheduler = BlockingScheduler(
        jobstores=jobstores,
        executors=executors,
        job_defaults=job_defaults,
        timezone=utc
    )
    
    try:
        scheduler.add_job( # type: ignore
            run_sync_job,
            trigger=CronTrigger.from_crontab(SYNC_CRON_SCHEDULE, timezone=utc), # type: ignore
            id='qargo_sync_job',
            name='Qargo Unavailability Sync',
            replace_existing=True
        )

        logger.info("Scheduler started. Press Ctrl+C to exit.")

        scheduler.start() # type: ignore

    except (KeyboardInterrupt, SystemExit):
        logger.info("Scheduler shutting down...")
        scheduler.shutdown() # type: ignore
        logger.info("Scheduler shut down gracefully.")
    except ValueError as e:
         logger.error(f"Error parsing .env variable: {e}")
    except Exception as e:
        logger.exception(f"An unexpected error occurred with the scheduler: {e}")
        if scheduler.running: # type: ignore
            scheduler.shutdown(wait=False) # type: ignore
