from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

LoanStatus = Literal["active", "returned", "overdue"]


class LoanCreate(BaseModel):
    user_id: int = Field(gt=0, examples=[1])
    device_id: int = Field(gt=0, examples=[3])


class LoanUpdate(BaseModel):
    status: LoanStatus
    return_date: Optional[datetime] = None


class LoanResponse(BaseModel):
    id: int
    user_id: int
    device_id: int
    loan_date: datetime
    return_date: Optional[datetime]
    status: LoanStatus

    model_config = ConfigDict(from_attributes=True)


class LoanUserSummary(BaseModel):
    id: int
    name: str
    email: str

    model_config = ConfigDict(from_attributes=True)


class LoanDeviceSummary(BaseModel):
    id: int
    name: str
    serial_number: str
    device_type: str

    model_config = ConfigDict(from_attributes=True)


class LoanDetailResponse(BaseModel):
    loan_id: int = Field(validation_alias="id")
    status: LoanStatus
    loan_date: datetime
    return_date: Optional[datetime]
    user: LoanUserSummary
    device: LoanDeviceSummary

    model_config = ConfigDict(from_attributes=True)