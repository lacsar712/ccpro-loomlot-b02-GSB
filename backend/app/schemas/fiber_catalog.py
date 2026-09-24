from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class FiberCatalogCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=64)
    is_active: bool = Field(default=True, alias="isActive")
    capacity_limit_l: float = Field(..., gt=0, alias="capacityLimitL")

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("name")
    @classmethod
    def strip_name(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("纤维名不能为空")
        return v


class FiberCatalogUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=64)
    is_active: Optional[bool] = Field(None, alias="isActive")
    capacity_limit_l: Optional[float] = Field(None, gt=0, alias="capacityLimitL")

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("name")
    @classmethod
    def strip_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        v = v.strip()
        if not v:
            raise ValueError("纤维名不能为空")
        return v


class FiberCatalogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    name: str
    is_active: bool = Field(serialization_alias="isActive")
    capacity_limit_l: float = Field(serialization_alias="capacityLimitL")
