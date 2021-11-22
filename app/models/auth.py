from app.db import Base, session
from sqlalchemy import Column, DateTime, Integer, String, ForeignKey, func, Boolean, Table
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID

user_group = Table(
    "user_group",
    Base.metadata,
    Column("user_uid", UUID(as_uuid=True),
           ForeignKey("users.uid"), primary_key=True),
    Column("group_uid", UUID(as_uuid=True),
           ForeignKey("groups.uid"), primary_key=True),
)


class Group(Base):
    name = Column(String(50), nullable=False)
    description = Column(String(255), nullable=True)
    users = relationship("User", secondary=user_group, back_populates="groups")

    def __repr__(self):
        return f"<Group(name={self.name})>"

    def __str__(self):
        return self.name


class User(Base):
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False)
    password = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)

    is_active = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    is_staff = Column(Boolean, default=False)
    date_joined = Column(DateTime(timezone=True), default=func.now())
    last_login = Column(DateTime(timezone=True), default=func.now())
    groups = relationship("Group", secondary="user_group",
                          back_populates="users")
    sessions = relationship("Session", back_populates="user")
    blogs = relationship("Blog", back_populates="user")

    def __repr__(self):
        return f"<User(first_name='{self.first_name}', last_name='{self.last_name}', email='{self.email}')>"

    def __str__(self):
        return f"<User(first_name='{self.first_name}', last_name='{self.last_name}', email='{self.email}')>"

    # Get the full name of the user
    @property
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"


# Session Model
class Session(Base):
    """
    Session Model for storing Session Data
    """
    user_uid = Column(UUID(as_uuid=True), ForeignKey(
        "users.uid"), nullable=False)
    user = relationship("User", back_populates="sessions")
    access_token = Column(String(500), unique=True, nullable=False)
    refresh_token = Column(String(500), unique=True, nullable=False)
    city = Column(String(50), nullable=True)
    region = Column(String(50), nullable=True)
    country = Column(String(50), nullable=True)
    ip_address = Column(String(50), nullable=True)
    timezone = Column(String(50), nullable=True)
    user_agent = Column(String(255), nullable=True)
    loc = Column(String(255), nullable=True)
