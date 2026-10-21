from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class AttendanceResponse(BaseModel):
    id: int
    employee_id: int
    attendance_date: date
    check_in: datetime | None = None
    check_out: datetime | None = None
    working_hours: Decimal | None = None
    status: str | None = None

    model_config = ConfigDict(from_attributes=True)