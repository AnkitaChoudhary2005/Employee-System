
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.utlis.db import get_db
from src.user.auth import get_current_user
from src.employee.attendance_schema import AttendanceResponse
from src.employee import attendance_controller as controller

router = APIRouter(prefix="/attendance", tags=["Attendance"])


# Employee checks in for themselves
@router.post("/check-in", response_model=AttendanceResponse)
def my_check_in(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    employee = controller.get_employee_for_user(current_user, db)
    return controller.check_in_employee(employee.id, db)


# Employee checks out for themselves
@router.put("/check-out", response_model=AttendanceResponse)
def my_check_out(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    employee = controller.get_employee_for_user(current_user, db)
    return controller.check_out_employee(employee.id, db)


# Admin checks in a selected employee
@router.post(
    "/employee/{employee_id}/check-in",
    response_model=AttendanceResponse,
)
def employee_check_in(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    employee = controller.get_authorized_employee(
        employee_id, current_user, db
    )
    return controller.check_in_employee(employee.id, db)


# Admin checks out a selected employee
@router.put(
    "/employee/{employee_id}/check-out",
    response_model=AttendanceResponse,
)
def employee_check_out(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    employee = controller.get_authorized_employee(
        employee_id, current_user, db
    )
    return controller.check_out_employee(employee.id, db)


# Employee views their own attendance history
@router.get("/me", response_model=list[AttendanceResponse])
def my_attendance(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    employee = controller.get_employee_for_user(current_user, db)
    return controller.get_attendance_history(employee.id, db)


# Admin views attendance for a selected employee
@router.get(
    "/employee/{employee_id}",
    response_model=list[AttendanceResponse],
)
def attendance_for_employee(
    employee_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    employee = controller.get_authorized_employee(
        employee_id, current_user, db
    )
    return controller.get_attendance_history(employee.id, db)


# Admin views all attendance records
@router.get("/", response_model=list[AttendanceResponse])
def attendance_list(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    role = str(
        controller.get_user_value(current_user, "role", "")
    ).strip().lower()

    if role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Only admins can view all attendance records",
        )

    return controller.get_all_attendance(db)
