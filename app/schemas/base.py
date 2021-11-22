from pydantic import BaseModel, Field
import datetime
from uuid import UUID


class BaseMeta(BaseModel):
    id: int = Field(..., title="Id")
    uid: UUID = Field(..., title="UUID")
    created_at: datetime.datetime = Field(
        datetime.datetime.now(), title="Created At")
    updated_at: datetime.datetime = Field(
        datetime.datetime.now(), title="Updated At")
