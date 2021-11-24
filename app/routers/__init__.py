from fastapi import APIRouter
# Import all routes
from .auth import router as auth_router
from .blog import router as blog_router

api_router = APIRouter()

api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(blog_router, prefix="/blog", tags=["blog"])
