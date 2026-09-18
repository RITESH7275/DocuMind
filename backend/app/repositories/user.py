from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


def get_user_by_email(
    db: Session,
    email: str,
):
    statement = select(User).where(
        User.email == email
    )

    return db.execute(
        statement
    ).scalar_one_or_none()


def get_user_by_id(
    db: Session,
    user_id: int,
):
    statement = select(User).where(
        User.id == user_id
    )

    return db.execute(
        statement
    ).scalar_one_or_none()


def create_user(
    db: Session,
    email: str,
    hashed_password: str,
):
    user = User(
        email=email,
        hashed_password=hashed_password,
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user