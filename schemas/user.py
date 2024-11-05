from pydantic import BaseModel
from datetime import datetime
from typing import Optional


def validate_user_create(data):
    # Add validation logic here
    if not data:
        abort(400, description="Invalid request data")
    # Add more specific validation as needed
    return data


def validate_user_update(data):
    # Add validation logic here
    if not data:
        abort(400, description="Invalid request data")
    # Add more specific validation as needed
    return data


class UserBase(BaseModel):
    name: str
    no_hp: Optional[str] = None
    take_date: Optional[datetime] = None
    image: str


class UserCreate(UserBase):
    pass


class UserUpdate(UserBase):
    pass


class UserInDB(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime] = None


class UserResponse(BaseModel):
    status: str
    message: str = None
    data: Optional[UserInDB] = None


class UsersListResponse(BaseModel):
    status: str
    data: list[UserInDB]
    pagination: dict
