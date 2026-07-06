from typing import Literal
from pydantic import BaseModel, Field

class RegisterRequest(BaseModel):
    username: str = Field(..., description="Unique enrollment ID, email, phone, or username")
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")
    role: Literal["STUDENT", "STAFF", "PARENT"] = Field(default="STUDENT")
    house_id: int | None = Field(default=None)
    section_id: int | None = Field(default=None)

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshRequest(BaseModel):
    refresh_token: str
