from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from domain.unavailability_reason import UnavailabilityReason
from models.unavailability import Unavailability

class UnavailabilityPostDto(BaseModel):
    external_id: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    reason: UnavailabilityReason
    description: Optional[str] = None

    @classmethod
    def from_unavailability(cls, unavailability: Unavailability) -> "UnavailabilityPostDto":
        return cls(
            external_id=unavailability.external_id,
            start_time=unavailability.start_time,
            end_time=unavailability.end_time,
            reason=unavailability.reason,
            description=unavailability.description,
        )