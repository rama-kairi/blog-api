from pydantic import BaseModel, Field
import datetime
from uuid import UUID


class BaseMeta(BaseModel):
    id: int = None
    uid: UUID = None
    created_at: datetime.datetime = Field(
        datetime.datetime.now(), title="Created At")
    updated_at: datetime.datetime = Field(
        datetime.datetime.now(), title="Updated At")
