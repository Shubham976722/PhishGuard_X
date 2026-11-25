
from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.api.dependencies import get_db, get_current_user
from backend.app.models.user import User

from backend.app.schemas.auth import (
    UserRegister,
    UserLogin,
    UserResponse,
    TokenResponse
)

from backend.app.services.auth_service import (
    register_user,
    authenticate_user
)


router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"]
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED
)
def register(data: UserRegister, db=Depends(get_db)):
    user = register_user(db, data)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    return user


@router.post(
    "/login",
    response_model=TokenResponse
)
def login(data: UserLogin, db=Depends(get_db)):
    result = authenticate_user(
        db,
        str(data.email),
        data.password
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    user, token = result

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@router.get(
    "/me",
    response_model=UserResponse
)
def get_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user
