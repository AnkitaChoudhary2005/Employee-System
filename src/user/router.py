from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from src.utlis.db import get_db
from src.user.schema import (
    UserLogin,
    TokenResponse,
    UserResponse,
)
from src.user.dtos import user_to_dto
from src.user.controller import (
    login_user,
    blacklisted_tokens,
)
from src.user.auth import (
    get_current_user,
    bearer_scheme,
)


router = APIRouter(
    prefix="/user",
    tags=["Users"],
)


# Login
@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    data: UserLogin,
    db: Session = Depends(get_db),
):
    return login_user(
        data.email,
        data.password,
        db,
    )


# Get logged-in user's account
@router.get(
    "/me",
    response_model=UserResponse,
)
def get_my_account(
    current_user=Depends(get_current_user),
):
    return user_to_dto(current_user)


# Logout
@router.post("/logout")
def logout(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    current_user=Depends(get_current_user),
):
    if credentials is None:
        raise HTTPException(
            status_code=401,
            detail="Authorization token is required",
        )

    blacklisted_tokens.add(credentials.credentials)

    return {
        "message": "Logout successful"
    }
