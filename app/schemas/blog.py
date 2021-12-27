import datetime
from typing import List, Optional
from pydantic import BaseModel, validator, EmailStr, SecretStr, Field
from uuid import UUID

from pydantic.networks import AnyHttpUrl
from .base import BaseMeta
from app import schemas


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
    name: str

    class Config:
        orm_mode = True


class BlogBase(BaseModel):
    title: str = None
    body: str = None
    featured_image: str = None
    is_featured: bool = False


class BlogIn(BlogBase):
    cat_id: UUID = None
    tags: List[UUID] = []


class blogUpdate(BaseModel):
    title: str = None
    body: str = None
    featured_image: str = None
    is_featured: bool = False
    cat_id: UUID = None
    user_id: UUID = None
    tags: List[UUID] = []


class BlogOut(BaseMeta, BlogBase):
    slug: Optional[str] = None
    user: schemas.auth.UserOut = {}
    category: CategoryOutforBlog = {}
    tags: List[TagOut] = []

    class Config:
        orm_mode = True


class BlogBaseOut(BaseModel):
    title: str = None
    body: str = None
    slug: str = None
    featured_image: AnyHttpUrl
    trend_rank: int = 0
    is_featured: bool = False

    class Config:
        orm_mode = True


class CategoryOut(CategoryIn, BaseMeta):
    blogs: List[BlogBaseOut] = []

    class Config:
        orm_mode = True


class TagOutMain(TagIn, BaseMeta):
    blogs: List[BlogBaseOut] = []

    class Config:
        orm_mode = True
