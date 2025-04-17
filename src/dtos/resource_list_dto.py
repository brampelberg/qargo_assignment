from typing import List, Optional
from pydantic import BaseModel
from dtos.resource_dto import ResourceDto

class ResourceListDto(BaseModel):
    next_cursor: Optional[str] = None
    items: List[ResourceDto]