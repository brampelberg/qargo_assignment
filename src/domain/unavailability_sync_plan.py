from typing import NamedTuple, Deque
from typing import Deque

from models.unavailability import Unavailability

class UnavailabilitySyncPlan(NamedTuple):
    to_create: Deque[Unavailability]
    to_update: Deque[Unavailability]
    to_delete: Deque[Unavailability]