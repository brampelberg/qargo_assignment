from typing import Optional
from pydantic import BaseModel, UUID4
from datetime import datetime
from domain.unavailability_reason import UnavailabilityReason
from dtos.unavailability_dto import UnavailabilityDto

class Unavailability(BaseModel):
    id: UUID4
    external_id: Optional[str] = None
    start_time: datetime
    end_time: Optional[datetime] = None
    reason: UnavailabilityReason
    description: Optional[str] = None

    @classmethod
    def from_unavailability_dto(cls, dto: UnavailabilityDto) -> "Unavailability":
        return cls(
            id=dto.id,
            external_id=dto.external_id,
            start_time=dto.start_time,
            end_time=dto.end_time,
            reason=dto.reason,
            description=dto.description,
        )
    
    def equals(self, other: "Unavailability") -> bool:
        return (
            self.start_time == other.start_time and
            self.end_time == other.end_time and
            self.reason == other.reason and
            self.description == other.description
        )
