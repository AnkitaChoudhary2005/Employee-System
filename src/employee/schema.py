
from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# Data required to create an employee
class EmployeeCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)

    salary: Decimal = Field(
        ge=0,
        max_digits=12,
        decimal_places=2,
    )

    department: str = Field(
        default="General",
        max_length=100,
    )


# Data allowed when updating an employee
class EmployeeUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=120,
    )

    salary: Decimal | None = Field(
        default=None,
        ge=0,
        max_digits=12,
        decimal_places=2,
    )

    department: str | None = Field(
        default=None,
        max_length=100,
    )

    email: EmailStr | None = None
    is_active: bool | None = None


# Employee data returned by the API
class EmployeeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    salary: Decimal
    department: str
    email: EmailStr | None = None
    is_active: bool = True

    # Accept the datetime value stored in the database
    date_of_joining: datetime | date | None = None

    is_updated: datetime | None = None
    role: str = "employee"
