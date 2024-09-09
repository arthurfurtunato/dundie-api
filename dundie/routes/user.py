from sqlmodel import Session, select
from dundie.db import ActiveSession
from dundie.models.user import User, UserResponse
from fastapi import APIRouter
from typing import List

router = APIRouter()

@router.get("/", response_model=List[UserResponse])
async def list_users(*, session: Session = ActiveSession):
  """List all users from database"""

  users = session.exec(select(User)).all()
  return users
