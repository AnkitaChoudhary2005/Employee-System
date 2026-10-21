
from datetime import date, datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.employee.models import EmployeeModel
from src.employee.dtos import employee_to_dto
from src.user.models import UserModel
from src.user.controller import hash_password


def create_employee(payload, db: Session):
    email = str(payload.email).strip().lower()
    name = payload.name.strip()
    department = (payload.department or "").strip() or "General"

    # Check whether this email already belongs to an employee.
    existing_employee = (
        db.query(EmployeeModel)
        .filter(EmployeeModel.email.ilike(email))
        .first()
    )

    if existing_employee:
        raise HTTPException(
            status_code=409,
            detail="This email already exists in the employee table.",
        )

    # Check whether this email already belongs to a login account.
    existing_user = (
        db.query(UserModel)
        .filter(UserModel.email.ilike(email))
        .first()
    )

    if existing_user:
        raise HTTPException(
            status_code=409,
            detail="This email already exists in the user login table.",
        )

    try:
        # Create the employee's login account.
        user = UserModel(
            name=name,
            email=email,
            password_hash=hash_password(payload.password),
            role="employee",
            is_active=True,
        )
        db.add(user)

        # Create the employee's employment record.
        employee = EmployeeModel(
            name=name,
            email=email,
            password=None,
            salary=payload.salary,
            department=department,
            is_active=True,
            date_of_joining=date.today(),
            is_updated=datetime.now(),
            role="employee",
        )
        db.add(employee)

        # Save both records together.
        db.commit()
        db.refresh(employee)

        return employee_to_dto(employee)

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Could not create employee and login account.",
        )


def get_all_employees(db: Session):
    employees = (
        db.query(EmployeeModel)
        .order_by(EmployeeModel.id)
        .all()
    )

    return [
        employee_to_dto(employee)
        for employee in employees
    ]


def get_employee_by_id(employee_id: int, db: Session):
    employee = (
        db.query(EmployeeModel)
        .filter(EmployeeModel.id == employee_id)
        .first()
    )

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found.",
        )

    return employee_to_dto(employee)


def update_employee(employee_id: int, payload, db: Session):
    employee = (
        db.query(EmployeeModel)
        .filter(EmployeeModel.id == employee_id)
        .first()
    )

    if not employee:
        raise HTTPException(
            status_code=404,
            detail="Employee not found.",
        )

    data = payload.model_dump(exclude_unset=True)

    original_email = employee.email

    user = (
        db.query(UserModel)
        .filter(UserModel.email == original_email)
        .first()
    )

    try:
        # Update email only when a new email was provided.
        if "email" in data and data["email"] is not None:
            new_email = str(data["email"]).strip().lower()

            if not new_email:
                raise HTTPException(
                    status_code=400,
                    detail="Email cannot be empty.",
                )

            duplicate_employee = (
                db.query(EmployeeModel)
                .filter(
                    EmployeeModel.email.ilike(new_email),
                    EmployeeModel.id != employee_id,
                )
                .first()
            )

            if duplicate_employee:
                raise HTTPException(
                    status_code=409,
                    detail="Email already belongs to another employee.",
                )

            duplicate_user_query = db.query(UserModel).filter(
                UserModel.email.ilike(new_email)
            )

            if user:
                duplicate_user_query = duplicate_user_query.filter(
                    UserModel.id != user.id
                )

            duplicate_user = duplicate_user_query.first()

            if duplicate_user:
                raise HTTPException(
                    status_code=409,
                    detail="Email already belongs to another user.",
                )

            employee.email = new_email

            if user:
                user.email = new_email

        # Update remaining employee fields.
        for key, value in data.items():
            if key == "email" or value is None:
                continue

            if key in ("name", "department"):
                value = value.strip()

            setattr(employee, key, value)

            if user and key == "name":
                user.name = value

            if user and key == "is_active":
                user.is_active = value

        employee.is_updated = datetime.now()

        db.commit()
        db.refresh(employee)

        return employee_to_dto(employee)

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Could not update employee.",
        )
