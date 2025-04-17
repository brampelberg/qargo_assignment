from typing import Dict, NamedTuple
from models.unavailability import Unavailability

class UnavailabilityGroups(NamedTuple):
    target_unavailabilities_with_external_id: Dict[str, Unavailability]
    target_unavailabilities_without_external_id: Dict[str, Unavailability]
    master_unavailabilities: Dict[str, Unavailability]