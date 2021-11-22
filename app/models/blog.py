from sqlalchemy.sql.expression import False
from app.db import Base, session
from sqlalchemy import Column, DateTime, Integer, String, ForeignKey, func, Boolean, Table
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID, base


class Category(Base):
    name = Column(String(50), nullable=False)
    description = Column(String(255), nullable=False)


class Blog(Base):
    title = Column(String(255), nullable=False)
    body = Column(String(5000), nullable=False)
    slug = Column(String(255), nullable=True)
    featured_image = Column(String(255), nullable=True)
    trend_rank = Column(Integer, nullable=False, default=0)
    is_featured = Column(Boolean, nullable=False, default=False)

    user_id = Column(UUID, ForeignKey('user.id'), nullable=False)
    user = relationship('User', back_populates='blogs')

    # Override save method
    def save(self):
        # to create slug on save if not slug is already created
        if not self.slug:
            self.slug = self.title.lower().replace(' ', '-')
        # to update trend rank on save
        self.trend_rank = self.trend_rank + 1
        super().save()
