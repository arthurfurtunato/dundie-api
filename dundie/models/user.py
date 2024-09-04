from typing import Optional
from sqlmodel import Field, SQLModel
from dundie.security import HashedPassword

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