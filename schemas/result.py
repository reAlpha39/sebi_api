from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from mysql.connector import Error


class ResultCreate(BaseModel):
    title: str
    description: Optional[str] = None


class ResultUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


class ResultResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
