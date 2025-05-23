"""
This type stub file was generated by pyright.
"""

from apscheduler.schedulers.base import BaseScheduler

class BlockingScheduler(BaseScheduler):
    """
    A scheduler that runs in the foreground
    (:meth:`~apscheduler.schedulers.base.BaseScheduler.start` will block).
    """
    _event = ...
    def start(self, *args, **kwargs): # -> None:
        ...
    
    def shutdown(self, wait=...): # -> None:
        ...
    
    def wakeup(self): # -> None:
        ...
    


