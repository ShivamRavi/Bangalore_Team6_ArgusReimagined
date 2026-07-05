import uuid
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class UserResponse(BaseModel):
    id: uuid.UUID
    username: str
    role: str
    house_id: int | None = None
    house_name: str | None = None
    section_id: int | None = None
    section_name: str | None = None
    euros_balance: int
    lifetime_euros: int
    current_planet: str
    current_streak: int
    last_active_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
