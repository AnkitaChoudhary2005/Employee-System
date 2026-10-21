from datetime import datetime, timezone
import logging

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.employee.leave_model import LeaveModel
from src.employee.models import EmployeeModel
from src.manager.models import ManagerModel

logger = logging.getLogger(__name__)


def user_value(user, key, default=None):
    if isinstance(user, dict):
        return user.get(key, default)
    return getattr(user, key, default)



def get_employee_for_user(user, db: Session):
    role = str(user_value(user, "role", "")).strip().lower()
    email = user_value(user, "email")

    # This function is only for an employee's own leave requests.
    if role not in ("employee", "user"):
        raise HTTPException(
            status_code=403,
            detail=(
                f"Only employees can access their own leave requests. "
                f"Current role: {role!r}. "
                "Admins and managers should use GET /leave/."
            ),
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

def get_leave_or_404(leave_id: int, db: Session):
    leave = (
        db.query(LeaveModel)
        .filter(LeaveModel.id == leave_id)
        .first()
    )

    if not leave:
        raise HTTPException(
            status_code=404,
            detail="Leave request not found",
        )

    return leave


def apply_for_leave(user, data, db: Session):
    employee = get_employee_for_user(user, db)

    if data.start_date > data.end_date:
        raise HTTPException(
            status_code=400,
            detail="Leave start date cannot be after its end date",
        )

    overlapping_leave = (
        db.query(LeaveModel)
        .filter(
            LeaveModel.employee_id == employee.id,
            LeaveModel.status.in_(["pending", "approved"]),
            LeaveModel.start_date <= data.end_date,
            LeaveModel.end_date >= data.start_date,
        )
        .first()
    )

    if overlapping_leave:
        raise HTTPException(
            status_code=400,
            detail=(
                "You already have a pending or approved leave request "
                "for these dates"
            ),
        )

    leave = LeaveModel(
        employee_id=employee.id,
        start_date=data.start_date,
        end_date=data.end_date,
        reason=data.reason.strip(),
        status="pending",
    )

    try:
        db.add(leave)
        db.commit()
        db.refresh(leave)
        return leave

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Could not submit leave request",
        )


def get_my_leaves(user, db: Session):
    employee = get_employee_for_user(user, db)

    return (
        db.query(LeaveModel)
        .filter(LeaveModel.employee_id == employee.id)
        .order_by(LeaveModel.created_at.desc())
        .all()
    )


def get_all_leaves(db: Session):
    return (
        db.query(LeaveModel)
        .order_by(LeaveModel.created_at.desc())
        .all()
    )


def get_manager_leaves(user, db: Session):
    role = str(user_value(user, "role", "")).lower()

    if role != "manager":
        raise HTTPException(
            status_code=403,
            detail="Manager access required",
        )

    manager_user_id = user_value(user, "id")

    manager = (
        db.query(ManagerModel)
        .filter(ManagerModel.user_id == manager_user_id)
        .first()
    )

    if not manager:
        raise HTTPException(
            status_code=404,
            detail="Manager profile not found",
        )

    # There is no employee-to-manager assignment relationship.
    # Therefore, managers can view all leave requests.
    return get_all_leaves(db)


def review_leave(leave_id: int, data, reviewer, db: Session):
    role = str(user_value(reviewer, "role", "")).lower()
    reviewer_id = user_value(reviewer, "id")

    if role not in ("admin", "manager"):
        raise HTTPException(
            status_code=403,
            detail="Only a manager or admin can review leave requests",
        )

    if reviewer_id is None:
        raise HTTPException(
            status_code=401,
            detail="Authenticated reviewer ID is missing",
        )

    leave = get_leave_or_404(leave_id, db)

    if leave.status != "pending":
        raise HTTPException(
            status_code=400,
            detail="This leave request has already been reviewed",
        )

    if data.status not in ("approved", "rejected"):
        raise HTTPException(
            status_code=400,
            detail="Review status must be approved or rejected",
        )

    if role == "manager":
        manager = (
            db.query(ManagerModel)
            .filter(
                ManagerModel.user_id == reviewer_id
            )
            .first()
        )

        if not manager:
            raise HTTPException(
                status_code=404,
                detail="Manager profile not found",
            )

        # Without employee-manager assignments, managers can review
        # any pending leave request.

    leave.status = data.status
    leave.review_note = (
        data.review_note.strip()
        if data.review_note and data.review_note.strip()
        else None
    )
    leave.reviewed_by = reviewer_id
    leave.reviewed_at = datetime.now(timezone.utc)

    try:
        db.commit()
        db.refresh(leave)
        return leave

    except Exception:
        logger.exception(
            "Could not update leave request %s for reviewer %s",
            leave_id,
            reviewer_id,
        )
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Could not update leave request",
        )


