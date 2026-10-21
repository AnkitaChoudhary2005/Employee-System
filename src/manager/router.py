from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.utlis.db import get_db
from src.user.auth import get_current_user, is_admin
from src.manager.schema import ManagerCreate, ManagerResponse
from src.manager import controller

router = APIRouter(
    prefix="/manager",
    tags=["Manager"],
)


# Admin: create a manager account
@router.post("/create_manager", response_model=ManagerResponse)
def create_manager(
    data: ManagerCreate,
    db: Session = Depends(get_db),
    admin=Depends(is_admin),
):
    return controller.create_manager(data, db)


# Admin: view all managers
@router.get("/", response_model=list[ManagerResponse])
def get_managers(
    db: Session = Depends(get_db),
    admin=Depends(is_admin),
):
    return controller.get_all_managers(db)


# Manager: view their own manager profile
@router.get("/me", response_model=ManagerResponse)
def get_my_manager_profile(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    if current_user.role != "manager":
        from fastapi import HTTPException

        raise HTTPException(
            status_code=403,
            detail="Manager access required",
        )

    return controller.get_manager_by_user_id(
        current_user.id,
        db,
    )
