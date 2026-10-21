from sqlalchemy import (
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.sql import func

from src.utlis.db import Base


class LeaveModel(Base):
    __tablename__ = "leave_requests"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)

    employee_id = Column(
        Integer,
        ForeignKey("employee.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)

    reason = Column(Text, nullable=False)

    status = Column(
        String(20),
        nullable=False,
        default="pending",
        index=True,
    )

    review_note = Column(Text, nullable=True)

    reviewed_by = Column(
        Integer,
        ForeignKey("user.id", ondelete="SET NULL"),
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    reviewed_at = Column(DateTime(timezone=True), nullable=True)