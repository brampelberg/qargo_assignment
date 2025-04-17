from typing import List, Optional
from pydantic import BaseModel
from dtos.unavailability_dto import UnavailabilityDto

class UnavailabilityListDto(BaseModel):
    next_cursor: Optional[str] = None
    items: List[UnavailabilityDto]