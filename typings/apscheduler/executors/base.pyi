"""
This type stub file was generated by pyright.
"""

from abc import ABCMeta

class MaxInstancesReachedError(Exception):
    def __init__(self, job) -> None:
        ...
    


class BaseExecutor(metaclass=ABCMeta):
    """Abstract base class that defines the interface that every executor must implement."""
    _scheduler = ...
    _lock = ...
    _logger = ...
    def __init__(self) -> None:
        ...
    
    def start(self, scheduler, alias): # -> None:
        """
        Called by the scheduler when the scheduler is being started or when the executor is being
        added to an already running scheduler.

        :param apscheduler.schedulers.base.BaseScheduler scheduler: the scheduler that is starting
            this executor
        :param str|unicode alias: alias of this executor as it was assigned to the scheduler

        """
        ...
    
    def shutdown(self, wait=...): # -> None:
        """
        Shuts down this executor.

        :param bool wait: ``True`` to wait until all submitted jobs
            have been executed
        """
        ...
    
    def submit_job(self, job, run_times): # -> None:
        """
        Submits job for execution.

        :param Job job: job to execute
        :param list[datetime] run_times: list of datetimes specifying
            when the job should have been run
        :raises MaxInstancesReachedError: if the maximum number of
            allowed instances for this job has been reached

        """
        ...
    


def run_job(job, jobstore_alias, run_times, logger_name): # -> list[Any]:
    """
    Called by executors to run the job. Returns a list of scheduler events to be dispatched by the
    scheduler.

    """
    ...

async def run_coroutine_job(job, jobstore_alias, run_times, logger_name): # -> list[Any]:
    """Coroutine version of run_job()."""
    ...

