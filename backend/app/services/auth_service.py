
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from backend.app.models.user import User
from backend.app.schemas.auth import UserRegister
from backend.app.utils.security import (
    hash_password,
    verify_password,
    create_access_token
)


def register_user(db: Session, user_data: UserRegister):
    email = str(user_data.email).lower()

    try:
        existing_user = db.query(User).filter(
            User.email == email
        ).first()

        if existing_user:
            return None

        user = User(
            full_name=user_data.full_name,
            email=email,
            hashed_password=hash_password(user_data.password)
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    except IntegrityError:
        db.rollback()

        # A concurrent registration may have inserted this email.
        existing_user = db.query(User).filter(
            User.email == email
        ).first()

        if existing_user:
            return None

        raise

    except SQLAlchemyError:
        db.rollback()
        raise


def authenticate_user(db: Session, email: str, password: str):
    try:
        user = db.query(User).filter(
            User.email == email.lower()
        ).first()

        if not user or not verify_password(
            password,
            user.hashed_password
        ):
            return None

        if not user.is_active:
            return None

        token = create_access_token(user.id)

        return user, token

    except SQLAlchemyError:
        db.rollback()
        raise
