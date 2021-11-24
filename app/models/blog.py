from app.db import Base, session
from sqlalchemy import Column, DateTime, Integer, String, ForeignKey, func, Boolean, Table
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy_utils import observes


class Category(Base):
    name = Column(String(50), nullable=False, unique=True)
    description = Column(String(255), nullable=True)
    blogs = relationship("Blog", back_populates="category")

    def __str__(self):
        return self.name


blog_tags = Table(
    'blog_tags', Base.metadata,
    Column('blog_uid', UUID(as_uuid=True), ForeignKey('blogs.uid')),
    Column('tag_uid', UUID(as_uuid=True), ForeignKey('tags.uid'))
)


class Tag(Base):
    name = Column(String(50), nullable=False, unique=True)
    blogs = relationship("Blog", secondary=blog_tags, back_populates="tags")

    def __str__(self):
        return self.name


class Blog(Base):
    title = Column(String(255), nullable=False, unique=True)
    body = Column(String(5000), nullable=False)
    slug = Column(String(255), nullable=True)
    featured_image = Column(String(255), nullable=True)
    trend_rank = Column(Integer, nullable=False, default=0)
    is_featured = Column(Boolean, nullable=False, default=False)

    cat_id = Column(UUID(as_uuid=True), ForeignKey('categories.uid'))
    category = relationship("Category", back_populates="blogs")
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.uid'))
    user = relationship('User', back_populates='blogs')
    tags = relationship("Tag", secondary=blog_tags, back_populates="blogs")

    # Override save method
    # def save(self):
    #     # to create slug on save if not slug is already created
    #     if not self.slug:
    #         self.slug = self.title.lower().replace(' ', '-')
    #     # to update trend rank on save
    #     self.trend_rank = self.trend_rank + 1
    #     super().save()

    @observes('title')
    def generate_slug(self, title):
        if not self.slug:
            self.slug = self.title.lower().replace(' ', '-')

    def __str__(self):
        return self.title
