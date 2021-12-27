from typing import List
from fastapi import (
    APIRouter,
    status,
    Depends,
    HTTPException,
    Request,
    BackgroundTasks,
    File,
    UploadFile,
)
from sqlalchemy.sql.functions import func
from sqlalchemy.orm import Session


from app.db.session import get_db
from .deps import validate_password, get_current_user, get_current_admin_user
from app import crud, models, schemas
from app.routers import deps

from sqlalchemy.exc import IntegrityError


router = APIRouter()


# Create Categories
@router.post(
    "/category",
    response_model=schemas.blog.CategoryOut,
    status_code=status.HTTP_201_CREATED,
)
def create_category(
    cat_in: schemas.blog.CategoryIn,
    db: Session = Depends(get_db),
    current_user: models.auth.User = Depends(get_current_user),
):
    try:
        return crud.blog.category.create(db=db, obj_in=cat_in)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Category already exists"
        )


# Create Tags
@router.post(
    "/tag", response_model=schemas.blog.TagOutMain, status_code=status.HTTP_201_CREATED
)
def create_tag(
    tag_in: schemas.blog.TagIn,
    db: Session = Depends(get_db),
    current_user: models.auth.User = Depends(get_current_user),
):
    try:
        return crud.blog.tags.create(db=db, obj_in=tag_in)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Tag already exists"
        )


# Create Blog
@router.post(
    "/blog", response_model=schemas.blog.BlogOut, status_code=status.HTTP_201_CREATED
)
def create_blog(
    blog_in: schemas.blog.BlogIn,
    current_user: models.auth.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    ## *featured_image* should be a base64 image starting with "data:image/jpeg;base64,/"
    ## *tags* will accept a list of tag *uid*
    """
    category = crud.blog.category.get_by_any(db=db, uid=blog_in.cat_id)

    if not category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cat Id does not exist"
        )

    for tag_uid in blog_in.tags:
        tags = crud.blog.tags.get_by_any(db, uid=tag_uid)
        if not tags:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Tag Id does not exist"
            )

    # Upload image to cloudinary and get url
    img_url = deps.upload_to_cloudinary(blog_in.featured_image)
    # Data with Image
    blog_in_data = blog_in.dict()
    blog_in_data["featured_image"] = img_url
    del blog_in_data["tags"]

    try:
        blog_ins = models.blog.Blog(**blog_in_data, user_id=current_user.id)
        blog_ins.tags.extend(
            [crud.blog.tags.get_by_any(db, uid=tag_uid) for tag_uid in blog_in.tags]
        )
        blog_in.cate
        db.add(blog_ins)
        db.commit()
        db.refresh(blog_ins)
        return blog_ins
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Blog already exists"
        )


# Get All Blogs
@router.get(
    "/blogs", response_model=List[schemas.blog.BlogOut], status_code=status.HTTP_200_OK
)
def get_all_blogs(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.blog.blog.get_multi(db=db, skip=skip, limit=limit)


# Get all blogs by user
@router.get(
    "/blogs/{user_uid}",
    response_model=List[schemas.blog.BlogOut],
    status_code=status.HTTP_200_OK,
)
def get_all_blogs_by_user(
    user_uid: str, skip: int = 0, limit: int = 100, db: Session = Depends(get_db)
):
    return crud.blog.blog.filter(
        db=db, user_id=user_uid, skip=skip, limit=limit, order_by="created_at"
    )


# Get All Categories


@router.get(
    "/categories",
    response_model=List[schemas.blog.CategoryOut],
    status_code=status.HTTP_200_OK,
)
def get_all_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.blog.category.get_multi(db=db, skip=skip, limit=limit)


# Get All Tags
@router.get(
    "/tags",
    response_model=List[schemas.blog.TagOutMain],
    status_code=status.HTTP_200_OK,
)
def get_all_tags(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.blog.tags.get_multi(db=db, skip=skip, limit=limit)


# Get Blog by uid
@router.get(
    "/blog/{uid}", response_model=schemas.blog.BlogOut, status_code=status.HTTP_200_OK
)
def get_blog_by_uid(uid: str, db: Session = Depends(get_db)):
    return crud.blog.blog.get_by_any(db=db, uid=uid)


# Get Category by uid
@router.get(
    "/category/{uid}",
    response_model=schemas.blog.CategoryOut,
    status_code=status.HTTP_200_OK,
)
def get_category_by_uid(uid: str, db: Session = Depends(get_db)):
    return crud.blog.category.get_by_any(db=db, uid=uid)


# Get Tag by uid
@router.get(
    "/tag/{uid}", response_model=schemas.blog.TagOutMain, status_code=status.HTTP_200_OK
)
def get_tag_by_uid(uid: str, db: Session = Depends(get_db)):
    return crud.blog.tags.get_by_any(db=db, uid=uid)


# Update Blog
@router.put(
    "/blog/{uid}", response_model=schemas.blog.BlogOut, status_code=status.HTTP_200_OK
)
def update_blog(
    uid: str,
    blog_in: schemas.blog.blogUpdate,
    db: Session = Depends(get_db),
    current_user: models.auth.User = Depends(get_current_user),
):
    """
    ## *featured_image* should be a base64 image starting with "data:image/jpeg;base64,/"
    ## *tags* will accept a list of tag *uid*
    """
    # Blog Instance
    blog_instance = crud.blog.blog.get_by_any(db=db, uid=uid)

    blog_update_obj = blog_in.dict(exclude_none=True)
    del blog_update_obj["tags"]
    if blog_in.featured_image:
        img_url = deps.upload_to_cloudinary(blog_in.featured_image)
        blog_update_obj["featured_image"] = img_url
    if blog_in.tags:
        blog_update_obj.tags.extend(
            [crud.blog.tags.get_by_any(db, uid=tag_uid) for tag_uid in blog_in.tags]
        )

    try:
        return crud.blog.blog.update(
            db=db, db_obj=blog_instance, obj_in=blog_update_obj
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Blog already exists"
        )


# update Category
@router.put(
    "/category/{uid}",
    response_model=schemas.blog.CategoryOut,
    status_code=status.HTTP_200_OK,
)
def update_category(
    uid: str,
    category_in: schemas.blog.CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: models.auth.User = Depends(get_current_user),
):
    return crud.blog.category.update(
        db=db,
        db_obj=crud.blog.category.get_by_any(db=db, uid=uid),
        obj_in=category_in.dict(exclude_none=True),
    )


# update Tag
@router.put(
    "/tag/{uid}", response_model=schemas.blog.TagOutMain, status_code=status.HTTP_200_OK
)
def update_tag(
    uid: str,
    tag_in: schemas.blog.TagUpdate,
    db: Session = Depends(get_db),
    current_user: models.auth.User = Depends(get_current_user),
):
    return crud.blog.tag.update(
        db=db,
        db_obj=crud.blog.tag.get_by_any(db=db, uid=uid),
        obj_in=tag_in.dict(exclude_none=True),
    )


# Delete Blog
@router.delete("/blog/{uid}", status_code=status.HTTP_200_OK)
def delete_blog(
    uid: str,
    db: Session = Depends(get_db),
    current_user: models.auth.User = Depends(get_current_user),
):
    return crud.blog.blog.remove(db=db, uid=uid)


# Delete Category
@router.delete("/category/{uid}", status_code=status.HTTP_200_OK)
def delete_category(
    uid: str,
    db: Session = Depends(get_db),
    current_user: models.auth.User = Depends(get_current_user),
):
    return crud.blog.category.remove(db=db, uid=uid)


# Delete Tag
@router.delete("/tag/{uid}", status_code=status.HTTP_200_OK)
def delete_tag(
    uid: str,
    db: Session = Depends(get_db),
    current_user: models.auth.User = Depends(get_current_user),
):
    return crud.blog.tags.remove(db=db, uid=uid)
