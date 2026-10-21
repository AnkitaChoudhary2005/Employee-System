from sqlalchemy import (
    Column,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)

from src.utlis.db import Base


class SalaryModel(Base):
    __tablename__ = "salary"

    __table_args__ = (
        UniqueConstraint(
            "employee_id",
            "month",
            "year",
            name="unique_employee_salary_per_month",
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        autoincrement=True,
    )

    employee_id = Column(
        Integer,
        ForeignKey("employee.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    month = Column(Integer, nullable=False)
    year = Column(Integer, nullable=False)

    monthly_salary = Column(
        Numeric(12, 2),
        nullable=False,
        default=0,
    )

    present_days = Column(Integer, nullable=False, default=0)
    half_days = Column(Integer, nullable=False, default=0)
    absent_days = Column(Integer, nullable=False, default=0)

    payable_days = Column(
        Numeric(6, 2),
        nullable=False,
        default=0,
    )

    final_salary = Column(
        Numeric(12, 2),
        nullable=False,
        default=0,
    )

    status = Column(
        String(20),
        nullable=False,
        default="pending",
    )
