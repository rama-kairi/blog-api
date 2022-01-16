# used to handle expiry time for tokens
from datetime import datetime, timedelta
from typing import Optional

import jwt  # used for encoding and decoding jwt tokens
from app import models
from app.core.conf import settings
from app.models.auth import Group, User
from app.schemas.auth import GroupsBase, SessionIn, Token, UserIn
from fastapi import HTTPException  # used to handle error handling
from passlib.context import CryptContext  # used for hashing the password
from pydantic import EmailStr
from sqlalchemy.orm import Session

from .base import CRUDBase


class AuthCrud(CRUDBase[User, UserIn, UserIn]):
    hasher = CryptContext(schemes=["bcrypt"])

    def hash_password(self, password):
        return self.hasher.hash(password)

    def verify_password(self, password, encoded_password):
        return self.hasher.verify(password, encoded_password)

    # Authenticate user and return boolean
    def authenticate(self, db: Session, email: EmailStr, password: str) -> bool:
        """
        ### Authenticate user
        """
        user = self.get_by_any(db, email=email)
        return bool(user and self.verify_password(password, user.password))

    def encode_jwt_token(self, email: str) -> str:
        """
        ### Encode JWT Token
        """
        payload = {
            "exp": datetime.utcnow()
            + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRATION_MINUTE),
            "iat": datetime.utcnow(),
            "scope": "access_token",
            "sub": email,
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    def decode_jwt_token(self, token):
        """
        ### Decode JWT Token
        """
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[
                    settings.JWT_ALGORITHM,
                ],
            )
            if payload["scope"] == "access_token":
                return payload["sub"]
            raise HTTPException(status_code=401, detail="Scope for the token is invalid")
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

    def encode_refresh_token(self, email: str) -> str:
        payload = {
            "exp": datetime.utcnow()
            + timedelta(minutes=settings.JWT_REFRESH_TOKEN_EXPIRATION_MINUTE),
            "iat": datetime.utcnow(),
            "scope": "refresh_token",
            "sub": email,
        }
        return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)

    def refresh_token(self, refresh_token):
        """
        ### Encode JWT Refresh Token
        """
        try:
            payload = jwt.decode(
                refresh_token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
            if payload["scope"] == "refresh_token":
                email = payload["sub"]
                access_token = self.encode_jwt_token(email)
                refresh_token = self.encode_refresh_token(email)
                return access_token, refresh_token, email
            raise HTTPException(status_code=401, detail="Invalid scope for token")
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Refresh token expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

    def generate_password_reset_token(self, email: str) -> str:
        """
        ### Encode password hash Token
        """
        delta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
        now = datetime.utcnow()
        expires = now + delta
        exp = expires.timestamp()
        return jwt.encode(
            {"exp": exp, "nbf": now, "sub": email},
            settings.JWT_SECRET_KEY,
            algorithm="HS256",
        )

    def verify_password_reset_token(self, token: str) -> Optional[str]:
        """
        ### Verify password hash Token
        """
        try:
            decoded_token = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=[
                    settings.JWT_ALGORITHM,
                ],
            )
            return decoded_token["sub"]
        except jwt.PyJWTError:
            return None


auth = AuthCrud(User)


# Group CRUD
class GroupCrud(CRUDBase[Group, GroupsBase, GroupsBase]):
    pass


group = GroupCrud(Group)


# SESSION CRUD
class SessionCrud(CRUDBase[Session, SessionIn, SessionIn]):
    pass


session = SessionCrud(models.auth.Session)
