from __future__ import annotations
from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict

from app.core.constants import ActivityType


class ActivityCompletionRequest(BaseModel):
    resource_id: UUID
    activity_type: ActivityType
    # Frontend-specific fields for earning calculation
    foreground_time_seconds: Optional[int] = Field(None, description="Time spent in foreground for podcasts")
    completed: Optional[bool] = Field(None, description="Whether video was completed")
    focus_interruptions: Optional[int] = Field(None, description="Number of focus interruptions for videos")
    reason: Optional[str] = None
    frontend_extras: Optional[dict] = None
    metadata: Optional[dict] = None

    @field_validator('foreground_time_seconds')
    @classmethod
    def validate_foreground_time(cls, v):
        if v is not None and v < 0:
            raise ValueError('foreground_time_seconds must be non-negative')
        return v

    @field_validator('focus_interruptions')
    @classmethod
    def validate_focus_interruptions(cls, v):
        if v is not None and v < 0:
            raise ValueError('focus_interruptions must be non-negative')
        return v

    model_config = ConfigDict(from_attributes=True)


class ActivityCompletionResponse(BaseModel):
    id: UUID
    user_id: UUID
    resource_id: UUID
    activity_type: ActivityType
    euros_awarded: int
    transaction_id: Optional[UUID]
    completed_at: datetime

    model_config = ConfigDict(from_attributes=True)
