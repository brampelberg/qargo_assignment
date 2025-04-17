from typing import Optional
from pydantic import BaseModel, UUID4
from datetime import datetime
from domain.unavailability_reason import UnavailabilityReason

class UnavailabilityDto(BaseModel):
    id: UUID4
    external_id: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    reason: UnavailabilityReason
    description: Optional[str] = None
