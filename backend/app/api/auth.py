from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.db.session import get_db
from app.repositories.user import (
    create_user,
    get_user_by_email,
)
from app.schemas.user import (
    Token,
    UserCreate,
    UserResponse,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    # Check whether the email is already registered
    existing_user = get_user_by_email(
        db,
        user_data.email,
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Hash the password before storing it
    hashed_password = hash_password(
        user_data.password
    )

    # Create the user
    user = create_user(
        db=db,
        email=user_data.email,
        hashed_password=hashed_password,
    )

    return user


@router.post(
    "/login",
    response_model=Token,
)
def login(
    user_data: UserCreate,
    db: Session = Depends(get_db),
):
    # Find user by email
    user = get_user_by_email(
        db,
        user_data.email,
    )

    # Do not reveal whether email or password was incorrect
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Verify password against stored hash
    if not verify_password(
        user_data.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Generate JWT access token
    access_token = create_access_token(
        user.id
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(
    current_user=Depends(get_current_user),
):
    return current_user