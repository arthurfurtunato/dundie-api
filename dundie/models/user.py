from typing import Optional
from sqlmodel import Field, SQLModel
from dundie.security import HashedPassword
from pydantic import BaseModel, root_validator

class User(SQLModel, table=True):
  id: Optional[int] = Field(default=None, primary_key=True)
  email: str = Field(unique=True, nullable=False)
  username: str = Field(unique=True, nullable=False)
  avatar: Optional[str] = None
  bio: Optional[str] = None
  password: HashedPassword
  name: str = Field(nullable=False)
  dept: str = Field(nullable=False)
  currency: str = Field(nullable=False)

  @property
  def superuser(self):
    return self.dept == "management"
  
def generate_username(name: str) -> str:
  """
  Generates a slug username from a name
  "Bruno Rocha" -> "bruno-rocha"
  "Arthur Furtunato" -> "arthur-furtunato"
  """
  return name.lower().replace(" ", "-")


class UserResponse(BaseModel):
  """Serializer for when we send a response to the client"""

  name: str
  username: str 
  dept: str
  avatar: Optional[str] = None
  bio: Optional[str] = None
  currency: str

class UserRequest(BaseModel):
  """Serializer from when we get the user data from the client"""

  name: str
  email: str
  dept: str
  password: str
  username: Optional[str] = None
  avatar: Optional[str] = None
  bio: Optional[str] = None
  currency: str = "USD"

  @root_validator(pre=True)
  def generate_username_if_not_set(cls, values):
    """Generates username"""
    
    if values.get("username") is None:
      values["username"] = generate_username(values["name"])
    return values