from decimal import Decimal, ROUND_HALF_UP

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.employee.models import EmployeeModel
from src.employee.attendance_model import AttendanceModel
from src.salary.models import SalaryModel


WORKING_DAYS_PER_MONTH = Decimal("25")


def generate_salary(employee_id: int, month: int, year: int, db: Session):
    employee = (
        db.query(EmployeeModel)
        .filter(EmployeeModel.id == employee_id)
        .first()
    )

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    if not employee.is_active:
        raise HTTPException(
            status_code=400,
            detail="Cannot generate salary for an inactive employee",
        )

    existing_salary = (
        db.query(SalaryModel)
        .filter(
            SalaryModel.employee_id == employee_id,
            SalaryModel.month == month,
            SalaryModel.year == year,
        )
        .first()
    )

    if existing_salary:
        raise HTTPException(
            status_code=409,
            detail="Salary has already been generated for this month",
        )

    attendance_records = (
        db.query(AttendanceModel)
        .filter(
            AttendanceModel.employee_id == employee_id,
            AttendanceModel.attendance_date.isnot(None),
        )
        .all()
    )

    # Only count attendance for the requested month and year.
    attendance_records = [
        record
        for record in attendance_records
        if record.attendance_date.month == month
        and record.attendance_date.year == year
    ]

    present_days = 0
    half_days = 0

    for record in attendance_records:
        status = (record.status or "").strip().lower()

        if status == "half_day":
            half_days += 1
        elif status in ("present", "late"):
            present_days += 1

    # Count Sundays and Saturdays as ordinary calendar days only if
    # your attendance system records them. This formula uses 25
    # standard payable working days for the monthly salary calculation.
    absent_days = max(
        0,
        25 - present_days - half_days,
    )

    payable_days = (
        Decimal(present_days) + Decimal(half_days) * Decimal("0.5")
    )

    monthly_salary = Decimal(str(employee.salary or 0))
    daily_salary = monthly_salary / WORKING_DAYS_PER_MONTH

    final_salary = (
        daily_salary * payable_days
    ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    salary = SalaryModel(
        employee_id=employee_id,
        month=month,
        year=year,
        monthly_salary=monthly_salary,
        present_days=present_days,
        half_days=half_days,
        absent_days=absent_days,
        payable_days=payable_days,
        final_salary=final_salary,
        status="generated",
    )

    try:
        db.add(salary)
        db.commit()
        db.refresh(salary)
        return salary
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Could not generate salary",
        )


def get_salary(employee_id: int, month: int, year: int, db: Session):
    salary = (
        db.query(SalaryModel)
        .filter(
            SalaryModel.employee_id == employee_id,
            SalaryModel.month == month,
            SalaryModel.year == year,
        )
        .first()
    )

    if not salary:
        raise HTTPException(
            status_code=404,
            detail="Salary record not found for this month",
        )

    return salary


def get_all_salaries(db: Session):
    return db.query(SalaryModel).order_by(
        SalaryModel.year.desc(),
        SalaryModel.month.desc(),
        SalaryModel.employee_id,
    ).all()
