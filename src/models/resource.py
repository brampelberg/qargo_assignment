from typing import List, Optional
from pydantic import BaseModel, UUID4
from domain.resource_type_enum import ResourceTypeEnum
from dtos.resource_dto import ResourceDto
from models.unavailability import Unavailability

class Resource(BaseModel):
    id: UUID4
    name: Optional[str] = None
    code: Optional[str] = None
    type: ResourceTypeEnum
    unavailabilities: List[Unavailability] = []

    @classmethod
    def from_resource_dto(cls, dto: ResourceDto) -> "Resource":
        return cls(
            id=dto.id,
            name=dto.name,
            code=dto.code,
            type=dto.type,
            unavailabilities=[]
        )
