from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.utlis.db import get_db
from src.user.auth import get_current_user
from src.salary import controller
from src.salary.schema import SalaryResponse

salary = APIRouter(
    prefix="/salary",
    tags=["Salary"],
)


# Admin: generate salary for an employee
@salary.post("/generate/{employee_id}", response_model=SalaryResponse)
def generate_employee_salary(
    employee_id: int,
    year: int,
    month: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != "admin":
        from fastapi import HTTPException
        raise HTTPException(
            status_code=403,
            detail="Only admin can generate salary",
        )

    return controller.generate_salary(employee_id, month, year, db)


# Admin or manager: view one employee's salary
# Employees can view only their own salary.
@salary.get("/salary/{employee_id}", response_model=SalaryResponse)
def get_employee_salary(
    employee_id: int,
    year: int,
    month: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    from fastapi import HTTPException
    from src.employee.models import EmployeeModel

    if current_user.role not in ("admin", "manager", "employee", "user"):
        raise HTTPException(status_code=403, detail="Access denied")

    if current_user.role in ("employee", "user"):
        employee = (
            db.query(EmployeeModel)
            .filter(EmployeeModel.email == current_user.email)
            .first()
        )

        if not employee or employee.id != employee_id:
            raise HTTPException(
                status_code=403,
                detail="You can only view your own salary",
            )

    return controller.get_salary(employee_id, month, year, db)


# Admin or manager: view all generated salary records
@salary.get("/", response_model=list[SalaryResponse])
def get_all_employee_salaries(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    from fastapi import HTTPException

    if current_user.role not in ("admin", "manager"):
        raise HTTPException(
            status_code=403,
            detail="Only admin or manager can view all salary records",
        )

    return controller.get_all_salaries(db)
