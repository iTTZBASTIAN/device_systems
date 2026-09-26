from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class DeviceCreate(BaseModel):
    name: str = Field(min_length=1, examples=["Laptop Lenovo ThinkPad"])
    serial_number: str = Field(min_length=1, examples=["LEN-2024-001"])
    device_type: str = Field(min_length=1, examples=["laptop"])
    brand: Optional[str] = Field(default=None, examples=["Lenovo"])


class DeviceUpdate(DeviceCreate):
    is_available: bool = True


class DevicePatch(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1)
    serial_number: Optional[str] = Field(default=None, min_length=1)
    device_type: Optional[str] = Field(default=None, min_length=1)
    brand: Optional[str] = None
    is_available: Optional[bool] = None


class DeviceResponse(DeviceCreate):
    id: int
    is_available: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)