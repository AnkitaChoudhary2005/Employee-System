from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class LeaveCreate(BaseModel):
    start_date: date
    end_date: date
    reason: str = Field(min_length=3, max_length=1000)

    @model_validator(mode="after")
    def validate_dates(self):
        if self.end_date < self.start_date:
            raise ValueError("End date cannot be before start date")
        return self


class LeaveReview(BaseModel):
    status: Literal["approved", "rejected"]
    review_note: str | None = Field(default=None, max_length=1000)


class LeaveResponse(BaseModel):
    id: int
    employee_id: int
    start_date: date
    end_date: date
    reason: str
    status: str
    review_note: str | None = None
    reviewed_by: int | None = None
    created_at: datetime
    reviewed_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
