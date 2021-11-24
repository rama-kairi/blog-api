from typing import Optional

from pydantic.networks import EmailStr
from app.core.conf import settings
# used to handle expiry time for tokens
from datetime import datetime, timedelta
from passlib.context import CryptContext  # used for hashing the password
from fastapi import HTTPException  # used to handle error handling
import jwt  # used for encoding and decoding jwt tokens
from .base import CRUDBase
from sqlalchemy.orm import Session
from app import models
from app import schemas


# Blog Crud
class BlogCrud(CRUDBase[models.blog.Blog, schemas.blog.BlogBase, schemas.blog.BlogBase]):
    pass


blog = BlogCrud(models.blog.Blog)


# Category Crud
class CategoryCrud(CRUDBase[models.blog.Category, schemas.blog.CategoryIn, schemas.blog.CategoryIn]):
    pass


category = CategoryCrud(models.blog.Category)


# Tag Crud
class TagCrud(CRUDBase[models.blog.Tag, schemas.blog.TagIn, schemas.blog.TagIn]):
    pass


tags = TagCrud(models.blog.Tag)
