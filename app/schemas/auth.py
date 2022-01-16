import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, SecretStr, validator

from .base import BaseMeta


class GroupsBase(BaseModel):
    name: str
    description: Optional[str] = None

    class Config:
        orm_mode = True


class GroupsIn(GroupsBase):
    pass


class UserBase(BaseModel):
    first_name: str = None
    last_name: str = None
    email: EmailStr = None
    phone: str = None


class UserIn(UserBase):
    password: str
    confirm_password: str = Field(..., alias="confirm_password")


class UserDb(UserBase):
    pass


class UserOut(BaseMeta, UserBase):
    is_active: bool = False
    is_superuser: bool = False
    is_staff: bool = False
    date_joined: datetime.datetime = Field(datetime.datetime.now(), title="Date Joined")
    last_login: datetime.datetime = Field(datetime.datetime.now(), title="Last Login")
    groups: Optional[List[GroupsBase]] = []

    class Config:
        orm_mode = True


class GroupsOut(BaseMeta, GroupsBase):
    users: Optional[List[UserOut]] = []

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


class TokensResponse(BaseModel):
    access_token: str
    refresh_token: str

    class Config:
        orm_mode = True
