from decimal import Decimal
from pydantic import BaseModel, ConfigDict, Field


class SalaryResponse(BaseModel):
    id: int
    employee_id: int
    month: int
    year: int
    monthly_salary: Decimal
    present_days: int
    half_days: int
    absent_days: int
    payable_days: Decimal
    final_salary: Decimal
    status: str

    model_config = ConfigDict(from_attributes=True)


class SalaryGenerateRequest(BaseModel):
    employee_id: int = Field(gt=0)
    month: int = Field(ge=1, le=12)
    year: int = Field(ge=2000, le=2100)
