from typing import Annotated, Optional

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

FiberName = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=64)
]


class FiberCatalogCreate(BaseModel):
    fiber_name: FiberName = Field(..., alias="fiberName")
    enabled: bool = True
    max_capacity_l: float = Field(..., gt=0, alias="maxCapacityL")

    model_config = ConfigDict(populate_by_name=True)


class FiberCatalogUpdate(BaseModel):
    fiber_name: Optional[FiberName] = Field(None, alias="fiberName")
    enabled: Optional[bool] = None
    max_capacity_l: Optional[float] = Field(None, gt=0, alias="maxCapacityL")

    model_config = ConfigDict(populate_by_name=True)


class FiberCatalogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    fiber_name: str = Field(serialization_alias="fiberName")
    enabled: bool
    max_capacity_l: float = Field(serialization_alias="maxCapacityL")
