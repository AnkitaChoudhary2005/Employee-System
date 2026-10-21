from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from src.utlis.db import get_db
from src.utlis.settings import settings
from src.user.models import UserModel
from src.user.controller import blacklisted_tokens


bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Authorization token is required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    if token in blacklisted_tokens:
        raise HTTPException(
            status_code=401,
            detail="Token has been logged out",
        )

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        user_id = int(payload.get("sub"))

    except (JWTError, TypeError, ValueError):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = (
        db.query(UserModel)
        .filter(UserModel.id == user_id)
        .first()
    )

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=401,
            detail="User not found or inactive",
        )

    return user


def is_admin(
    current_user=Depends(get_current_user),
):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin access required",
        )

    return current_user


def is_manager(
    current_user=Depends(get_current_user),
):
    if current_user.role != "manager":
        raise HTTPException(
            status_code=403,
            detail="Manager access required",
        )

    return current_user


def is_employee(
    current_user=Depends(get_current_user),
):
    if current_user.role not in ("employee", "user"):
        raise HTTPException(
            status_code=403,
            detail="Employee access required",
        )

    return current_user
