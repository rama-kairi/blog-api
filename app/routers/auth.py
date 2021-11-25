from fastapi import APIRouter, status, Depends, HTTPException, Request, BackgroundTasks
from sqlalchemy.sql.functions import func
from app.schemas.auth import UserOut, UserIn, UserDb, Login, Token
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.auth import User
from app import crud
from .deps import validate_password, get_current_user
from app import models

from app.routers import deps

router = APIRouter()


@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def signup(user_obj: UserIn, db: Session = Depends(get_db),):
    # Check if the user already exists
    user = crud.auth.auth.get_by_any(db, email=user_obj.email)
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Another user already registered with same email.")

    # Perform Password Validation
    isPassValid, errors = validate_password(user_obj.password)
    if not isPassValid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=errors)

    # Check if password and confirm_password are same
    if user_obj.password != user_obj.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Password and Confirm Password are not same.")

    # If all validations are passed, hash the password
    hashed_password = crud.auth.auth.hash_password(user_obj.password)

    # Create User dict
    db_user = User(**UserDb(**user_obj.dict()).dict(),
                   password=hashed_password)
    # Create a 'user' group if not created and set the user to 'user' Group
    user_group = crud.auth.group.get_or_create(db, name='user')

    # Add user to 'user' group
    db_user.groups.append(user_group)
    db_user.is_active = True
    db_user.is_staff = True

    # Create User
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return db_user


# Login
@router.post("/login", status_code=status.HTTP_200_OK)
def login(bt: BackgroundTasks, user: Login, request: Request, db: Session = Depends(get_db)):
    user_instance = crud.auth.auth.get_by_any(db, email=user.email)
    if not user_instance:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Incorrect email or password")
    # Check if the user is active
    if not user_instance.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Your Account is not Active, Please check your email and confirm")
    # Check if user is Staff
    if not user_instance.is_staff:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="You are not authorize to login to dashboard")
        # Check user is in user Group
    user_groups = [g.name for g in user_instance.groups]
    if 'user' not in user_groups:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Only User Can Login in this Panel.")
    # Authenticate User with email and password
    isAuthenticated = crud.auth.auth.authenticate(
        db, email=user.email, password=user.password)
    if not isAuthenticated:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Email or Password is incorrect.")

    # Generate Access & Refresh Tokens
    access_token = crud.auth.auth.encode_jwt_token(user.email)
    refresh_token = crud.auth.auth.encode_refresh_token(user.email)

    # Update Last Login
    crud.auth.auth.update(db=db, db_obj=user_instance,
                          obj_in={'last_login': func.now()})

    # Create Sessions
    # session_data = deps.create_session(
    #     access_token, refresh_token, user.email, request, db)

    bt.add_task(deps.create_session,
                access_token, refresh_token, user.email, request, db)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


# User me route
@router.get("/me", response_model=UserOut, status_code=status.HTTP_200_OK)
def me(current_user: models.auth.User = Depends(get_current_user)):
    return current_user


# Logout
@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(token: Token, db: Session = Depends(get_db), current_user: UserOut = Depends(get_current_user)):
    # res = crud.session.delete_by_any(db, token=token.token)
    crud.auth.session.delete_by_any(db, access_token=token.access_token)
    # print(res)
    return {"message": "Successfully logged out."}


# Refresh API
@router.get("/refresh/{refresh_token}", status_code=status.HTTP_200_OK)
def refresh(refresh_token: str, db: Session = Depends(get_db)):
    # Check if the token is in blacklist
    is_refresh_token_valid = db.query(
        models.auth.Session).filter_by(refresh_token=refresh_token).first()
    if not is_refresh_token_valid:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Token Invalid.")

    # Generate Access & Refresh Tokens
    access_token, refresh_token, _ = crud.auth.auth.refresh_token(
        refresh_token)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }
