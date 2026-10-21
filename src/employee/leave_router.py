from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.utlis.db import get_db
from src.user.auth import get_current_user
from src.employee.leave_schema import (
    LeaveCreate,
    LeaveReview,
    LeaveResponse,
)
from src.employee import leave_controller as controller

router = APIRouter(
    prefix="/leave",
    tags=["Leave Management"],
)


@router.post("/apply", response_model=LeaveResponse)
def apply_leave(
    data: LeaveCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return controller.apply_for_leave(current_user, data, db)


@router.get("/me", response_model=list[LeaveResponse])
def my_leave_requests(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return controller.get_my_leaves(current_user, db)


@router.get("/", response_model=list[LeaveResponse])
def list_leave_requests(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    role = controller.user_value(current_user, "role", "")

    if role == "admin":
        return controller.get_all_leaves(db)

    if role == "manager":
        return controller.get_manager_leaves(current_user, db)

    raise HTTPException(
        status_code=403,
        detail="Use /leave/me to view your own leave requests",
    )


@router.put("/{leave_id}/review", response_model=LeaveResponse)
def review_leave_request(
    leave_id: int,
    data: LeaveReview,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return controller.review_leave(
        leave_id,
        data,
        current_user,
        db,
    )