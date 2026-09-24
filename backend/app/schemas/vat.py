from typing import Optional, Literal, Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

VatStatus = Literal["ready", "dyeing", "drain"]

FiberType = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=64)]


class VatCreate(BaseModel):
    dye_house_id: int = Field(..., alias="dyeHouseId")
    vat_code: str = Field(..., min_length=1, max_length=64, alias="vatCode")
    fiber_type: FiberType = Field(..., alias="fiberType")
    capacity_l: float = Field(..., gt=0, alias="capacityL")
    status: VatStatus = "ready"

    model_config = ConfigDict(populate_by_name=True)


class VatUpdate(BaseModel):
    dye_house_id: Optional[int] = Field(None, alias="dyeHouseId")
    vat_code: Optional[str] = Field(None, min_length=1, max_length=64, alias="vatCode")
    fiber_type: Optional[FiberType] = Field(None, alias="fiberType")
    capacity_l: Optional[float] = Field(None, gt=0, alias="capacityL")
    status: Optional[VatStatus] = None

    model_config = ConfigDict(populate_by_name=True)


class VatOut(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    dye_house_id: int = Field(serialization_alias="dyeHouseId")
    vat_code: str = Field(serialization_alias="vatCode")
    fiber_type: str = Field(serialization_alias="fiberType")
    capacity_l: float = Field(serialization_alias="capacityL")
    status: VatStatus
