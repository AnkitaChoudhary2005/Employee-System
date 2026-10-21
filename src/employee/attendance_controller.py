from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.employee.attendance_model import AttendanceModel
from src.employee.models import EmployeeModel


def get_user_value(user, key, default=None):
    if isinstance(user, dict):
        return user.get(key, default)
    return getattr(user, key, default)



def get_employee_for_user(user, db: Session):
    role = str(get_user_value(user, "role", "")).strip().lower()
    email = get_user_value(user, "email")

    # Allow employee role names used in this project.
    if role not in ("employee", "user"):
        raise HTTPException(
            status_code=403,
            detail=f"Only employees can use their own attendance endpoints. Current role: {role!r}",
        )

    if not email:
        raise HTTPException(
            status_code=401,
            detail="Logged-in user has no email",
        )

    employee = (
        db.query(EmployeeModel)
        .filter(EmployeeModel.email.ilike(email.strip()))
        .first()
    )

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee profile not found for this email",
        )

    if not employee.is_active:
        raise HTTPException(
            status_code=403,
            detail="This employee account is inactive",
        )

    return employee



def get_authorized_employee(employee_id: int, user, db: Session):
    role = str(get_user_value(user, "role", "")).strip().lower()

    # Admin can select any existing active employee.
    if role == "admin":
        employee = (
            db.query(EmployeeModel)
            .filter(EmployeeModel.id == employee_id)
            .first()
        )

        if not employee:
            raise HTTPException(
                status_code=404,
                detail="Employee not found",
            )

        if not employee.is_active:
            raise HTTPException(
                status_code=403,
                detail="This employee account is inactive",
            )

        return employee

    # Employees can only access their own attendance.
    if role in ("employee", "user"):
        employee = get_employee_for_user(user, db)

        if employee.id != employee_id:
            raise HTTPException(
                status_code=403,
                detail="Employees can only access their own attendance",
            )

        return employee

    raise HTTPException(
        status_code=403,
        detail="You are not allowed to access this employee's attendance",
    )

def check_in_employee(employee_id: int, db: Session):
    today = date.today()

    attendance = (
        db.query(AttendanceModel)
        .filter(
            AttendanceModel.employee_id == employee_id,
            AttendanceModel.attendance_date == today,
        )
        .first()
    )

    if attendance and attendance.check_in:
        raise HTTPException(
            status_code=400,
            detail="Employee has already checked in today",
        )

    now = datetime.now()

    if not attendance:
        attendance = AttendanceModel(
            employee_id=employee_id,
            attendance_date=today,
            check_in=now,
            working_hours=Decimal("0.00"),
            status="present",
        )
        db.add(attendance)
    else:
        attendance.check_in = now
        attendance.status = "present"

    try:
        db.commit()
        db.refresh(attendance)
        return attendance
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Could not save check-in",
        )


def check_out_employee(employee_id: int, db: Session):
    today = date.today()

    attendance = (
        db.query(AttendanceModel)
        .filter(
            AttendanceModel.employee_id == employee_id,
            AttendanceModel.attendance_date == today,
        )
        .first()
    )

    if not attendance or not attendance.check_in:
        raise HTTPException(
            status_code=400,
            detail="Employee must check in before checking out",
        )

    if attendance.check_out:
        raise HTTPException(
            status_code=400,
            detail="Employee has already checked out today",
        )

    checkout_time = datetime.now()

    if checkout_time < attendance.check_in:
        raise HTTPException(
            status_code=400,
            detail="Check-out cannot be earlier than check-in",
        )

    total_seconds = (
        checkout_time - attendance.check_in
    ).total_seconds()

    hours = Decimal(
        str(total_seconds / 3600)
    ).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )

    attendance.check_out = checkout_time
    attendance.working_hours = hours

    try:
        db.commit()
        db.refresh(attendance)
        return attendance
    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Could not save check-out",
        )


def get_attendance_history(employee_id: int, db: Session):
    return (
        db.query(AttendanceModel)
        .filter(AttendanceModel.employee_id == employee_id)
        .order_by(AttendanceModel.attendance_date.desc())
        .all()
    )


def get_all_attendance(db: Session):
    return (
        db.query(AttendanceModel)
        .order_by(AttendanceModel.attendance_date.desc())
        .all()
    )


def get_user_value_for_router(user, key, default=None):
    return get_user_value(user, key, default)
