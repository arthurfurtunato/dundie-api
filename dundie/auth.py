from datetime import timedelta, datetime
from typing import Optional, Callable, Union
from fastapi import Depends, HTTPException, Request, status
from jose import JWTError, jwt
from pydantic import BaseModel
from dundie.config import settings
from functools import partial
from fastapi.security import OAuth2PasswordBearer

from dundie.models.user import User
from dundie.security import verify_password
from dundie.db import engine
from sqlmodel import Session, select

ALGORITHM = settings.security.ALGORITHM
SECRET_KEY = settings.security.SECRET_KEY

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Models

class Token(BaseModel):
  access_token: str
  token_type: str
  refresh_token: str

class RefreshToken(BaseModel):
  refresh_token: str

class TokenData(BaseModel):
  username: Optional[str] = None

# Funcions

def create_access_token(
  data: dict,
  expires_delta: Optional[timedelta] = None,
  scope: str = "access_token"
) -> str:
  """Create a JWT Token"""

  to_encode = data.copy()
  expires_delta = expires_delta or timedelta(minutes=15)
  expire = datetime.now() + expires_delta
  to_encode.update({"exp": expire, "scope": scope})

  encoded_jwt = jwt.encode(
    to_encode,
    SECRET_KEY,
    ALGORITHM
  )

  return encoded_jwt

create_refresh_token = partial(create_access_token, scope="refresh_token")

def authenticate_user(get_user: Callable, username: str, password: str) -> Union[User, bool]:
  """verifies the user exists and password is correct"""
  user = get_user(username)

  if not user:
    return False

  if not verify_password(password, user.password):
    return False
  
  return user

def get_user(username: str) -> Optional[User]:
  """Get a user by username"""
  # TODO - Mover para um módulo de utilidades
  query = select(User).where(User.username == username)
  with Session(engine) as session:
    return session.exec(query).first()
  
def get_current_user(
    token: str = Depends(oauth2_scheme),
    request: Request = None,
    fresh = False
  ) -> User:
  """Get the current user from a token"""
  creadential_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})

  if request:
    if authorization := request.headers.get("Authorization"):
      try:
        token = authorization.split(" ")[1]
      except IndexError:
        raise creadential_exception

  try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username = payload.get("sub")
    if username is None:
      raise creadential_exception
    token_data = TokenData(username=username)
  except JWTError:
    raise creadential_exception
  
  user = get_user(username=token_data.username)
  if user is None:
    raise creadential_exception
  
  if fresh and (not payload["fresh"] and not user.superuser):
    raise creadential_exception
  
  return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
  """Wraps the sync get_active_user for sync calls"""
  return current_user

AuthenticatedUser = Depends(get_current_active_user)

async def get_current_super_user(
    current_user: User = Depends(get_current_user),
) -> User:
  """Wraps the sync get_active_user for sync calls for superuser"""
  if not current_user.superuser:
    raise HTTPException(
      status_code=status.HTTP_403_FORBIDDEN,
      detail="Not a superuser"
    )
  return current_user

SuperUser = Depends(get_current_super_user)

async def validate_token(token: str = Depends(oauth2_scheme)) -> User:
  user = get_current_user(token=token)
  return user