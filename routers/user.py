from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from datetime import datetime
from schemas.user import UserCreate, UserUpdate, UserResponse, UsersListResponse
from models.user import UserModel

router = APIRouter(
    prefix="/sebi-api",
    tags=["users"]
)


@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate):
    created_user = await UserModel.create_user(user.model_dump())
    return {
        "status": "success",
        "message": "User successfully created",
        "data": created_user
    }


@router.get("/", response_model=UsersListResponse)
async def get_users(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    include_deleted: bool = Query(False),
    search: Optional[str] = Query(None),
    from_date: Optional[datetime] = Query(None),
    to_date: Optional[datetime] = Query(None)
):
    users, total_records = await UserModel.get_users(
        page, limit, include_deleted, search, from_date, to_date
    )

    total_pages = (total_records + limit - 1) // limit

    return {
        "status": "success",
        "data": users,
        "pagination": {
            "total_records": total_records,
            "total_pages": total_pages,
            "current_page": page,
            "limit": limit,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user: UserUpdate):
    updated_user = await UserModel.update_user(user_id, user.model_dump())
    return {
        "status": "success",
        "message": "User successfully updated",
        "data": updated_user
    }


@router.delete("/{user_id}")
async def delete_user(user_id: int):
    return await UserModel.delete_user(user_id)
