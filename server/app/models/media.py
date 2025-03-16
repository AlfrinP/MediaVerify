from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class MediaType(str, Enum):
    IMAGE = "image"
    AUDIO = "audio"


class MediaStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class MediaBase(BaseModel):
    filename: str
    file_type: MediaType
    file_size: int
    mime_type: str
    description: Optional[str] = None


class MediaCreate(MediaBase):
    user_id: str
    s3_key: str


class MediaInDB(MediaBase):
    id: str = Field(alias="_id")
    user_id: str
    s3_key: str
    status: MediaStatus = MediaStatus.PENDING
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    reviewed_at: Optional[datetime] = None
    reviewed_by: Optional[str] = None
    review_notes: Optional[str] = None


class Media(MediaBase):
    id: str = Field(alias="_id")
    user_id: str
    status: MediaStatus
    uploaded_at: datetime
    reviewed_at: Optional[datetime]
    review_notes: Optional[str]

    class Config:
        from_attributes = True


class MediaUpdate(BaseModel):
    status: MediaStatus
    review_notes: Optional[str] = None
