from datetime import datetime

from fastapi import HTTPException
from pwdlib import PasswordHash
from sqlalchemy.orm import Session

from src.user.models import UserModel
from src.employee.models import EmployeeModel

password_hasher = PasswordHash.recommended()


def update_account(user_id: int, data, db: Session):
    user = (
        db.query(UserModel)
        .filter(UserModel.id == user_id)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    try:
        password_is_valid = password_hasher.verify(
            data.current_password,
            user.password_hash,
        )
    except Exception:
        password_is_valid = False

    if not password_is_valid:
        raise HTTPException(
            status_code=400,
            detail="Current password is incorrect",
        )

    try:
        if data.new_email:
            new_email = str(data.new_email).lower().strip()

            existing_user = (
                db.query(UserModel)
                .filter(
                    UserModel.email == new_email,
                    UserModel.id != user_id,
                )
                .first()
            )

            if existing_user:
                raise HTTPException(
                    status_code=409,
                    detail="This email is already registered",
                )

            employee = (
                db.query(EmployeeModel)
                .filter(EmployeeModel.email == user.email)
                .first()
            )

            if employee:
                duplicate_employee = (
                    db.query(EmployeeModel)
                    .filter(
                        EmployeeModel.email == new_email,
                        EmployeeModel.id != employee.id,
                    )
                    .first()
                )

                if duplicate_employee:
                    raise HTTPException(
                        status_code=409,
                        detail="This email belongs to another employee",
                    )

                employee.email = new_email
                employee.is_updated = datetime.now()

            user.email = new_email

        if data.new_password:
            user.password_hash = password_hasher.hash(
                data.new_password
            )

        db.commit()
        db.refresh(user)

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Could not update account",
        )

    return {
        "message": "Account updated successfully",
        "email": user.email,
    }
