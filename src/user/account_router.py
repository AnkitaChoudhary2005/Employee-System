from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from src.utlis.db import get_db
from src.user.auth import get_current_user
from src.user.account_schema import UpdateAccountSchema
from src.user.account_controller import update_account

router = APIRouter(
    prefix="/user",
    tags=["User Account"]
)


@router.put("/update-account")
def update_my_account(
    data: UpdateAccountSchema,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Supports authentication functions that return a dictionary
    # or a UserModel object.
    if isinstance(current_user, dict):
        user_id = current_user.get("id")
    else:
        user_id = current_user.id

    return update_account(user_id, data, db)