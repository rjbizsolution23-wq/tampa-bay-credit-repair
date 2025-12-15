from typing import Any, List

from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.api.routes import deps
# We need to create deps.py for current_user dependency
# For now, let's create a stub or inline it, but best practice is deps.py
from app.core.security import get_password_hash # If updating password

router = APIRouter()

# Placeholder for dependency until deps.py is created
# Ideally in app/api/routes/deps.py:
# def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> User
# For now we will assume the dependency exists or create it next.

@router.get("/me", response_model=Any) # Should use User Schema
def read_user_me(
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user

@router.get("/{user_id}", response_model=Any)
def read_user_by_id(
    user_id: str,
    current_user: User = Depends(deps.get_current_active_superuser),
    db: Session = Depends(get_db),
) -> Any:
    """
    Get a specific user by id.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if user == current_user:
        return user
    if not deps.is_superuser(current_user):
         raise HTTPException(status_code=400, detail="The user doesn't have enough privileges")
    return user
