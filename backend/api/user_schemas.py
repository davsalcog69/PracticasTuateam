from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class UserCreate(BaseModel):
    username: str
    password: str
    full_name: Optional[str] = None
    is_admin: bool = False

# User Profile Schemas
class UserOut(BaseModel):
    id: int
    username: str
    full_name: Optional[str] = None
    avatar: str
    is_admin: bool
    created_at: datetime

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    avatar: Optional[str] = None

class PasswordUpdate(BaseModel):
    current_password: str
    new_password: str

# Activity Schemas
class RecentCarOut(BaseModel):
    car_id: str
    model_name: Optional[str] = None
    viewed_at: datetime

    class Config:
        from_attributes = True
