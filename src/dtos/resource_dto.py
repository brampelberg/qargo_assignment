from typing import Optional
from pydantic import BaseModel, UUID4
from domain.resource_type_enum import ResourceTypeEnum

class ResourceDto(BaseModel):
    id: UUID4
    name: Optional[str] = None
    code: Optional[str] = None
    type: ResourceTypeEnum