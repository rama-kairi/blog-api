import datetime
from typing import List, Optional
from uuid import UUID

from app import schemas
from pydantic import BaseModel, EmailStr, Field, SecretStr, validator
from pydantic.networks import AnyHttpUrl

from .base import BaseMeta


class CategoryIn(BaseModel):
    name: str = None
    description: Optional[str] = None


class CategoryUpdate(BaseModel):
    name: str = None
    description: Optional[str] = None


class CategoryOutforBlog(BaseModel):
    name: str
    description: Optional[str] = None

    class Config:
        orm_mode = True


class TagIn(BaseModel):
    name: str = None


class TagUpdate(BaseModel):
    name: str = None


class TagOut(BaseModel):
    name: Optional[str] = None

    class Config:
        orm_mode = True


class BlogBase(BaseModel):
    title: str = None
    body: str = None
    featured_image: Optional[AnyHttpUrl] = None
    is_featured: bool = False


class BlogIn(BlogBase):
    cat_id: UUID = None
    tags: List[UUID] = []


class blogUpdate(BaseModel):
    title: str = None
    body: str = None
    featured_image: Optional[AnyHttpUrl] = None
    is_featured: bool = False
    cat_id: UUID = None
    user_id: UUID = None
    tags: List[UUID] = []


class BlogOut(BaseMeta, BlogBase):
    slug: Optional[str] = None
    user: schemas.auth.UserOut = {}
    category: Optional[CategoryOutforBlog] = {}
    tags: Optional[List[TagOut]] = []

    class Config:
        orm_mode = True


class BlogBaseOut(BaseModel):
    title: str = None
    body: str = None
    slug: str = None
    featured_image: Optional[AnyHttpUrl] = None
    trend_rank: int = 0
    is_featured: bool = False

    class Config:
        orm_mode = True


class CategoryOut(CategoryIn, BaseMeta):
    blogs: Optional[List[BlogBaseOut]] = []

    class Config:
        orm_mode = True


class TagOutMain(TagIn, BaseMeta):
    blogs: List[BlogBaseOut] = []

    class Config:
        orm_mode = True
