import datetime
from typing import List, Optional
from pydantic import BaseModel, validator, EmailStr, SecretStr, Field
from uuid import UUID
from .base import BaseMeta


class GroupsBase(BaseModel):
    name: str
    description: Optional[str] = None

    class Config:
        orm_mode = True


class GroupsIn(GroupsBase):
    pass


class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: str = None


class UserIn(UserBase):
    password: str
    confirm_password: str = Field(..., alias='confirm_password')


class UserDb(UserBase):
    pass


class UserOut(BaseMeta, UserBase):
    is_active: bool
    is_superuser: bool
    is_staff: bool
    date_joined: datetime.datetime
    last_login: datetime.datetime
    groups: List[GroupsBase] = []

    class Config:
        orm_mode = True


class GroupsOut(BaseMeta, GroupsBase):
    users: List[UserOut] = []

    class Config:
        orm_mode = True


class Login(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str


class SessionIn(BaseModel):
    user_uid: UUID
    access_token: str
    refresh_token: str
    city: Optional[str] = None
    region: Optional[str] = None
    country: Optional[str] = None
    ip_address: Optional[str] = None
    timezone: Optional[str] = None
    user_agent: Optional[str] = None
    loc: Optional[str] = None
