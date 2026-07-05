from typing import Literal
from pydantic import BaseModel, Field, model_validator

class RegisterRequest(BaseModel):
    username: str = Field(..., description="Unique enrollment ID, email, phone, or username")
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")
    role: Literal["STUDENT", "STAFF", "PARENT"] = Field(default="STUDENT")
    house_id: int | None = Field(default=None)
    section_id: int | None = Field(default=None)

    @model_validator(mode="after")
    def validate_student_fields(self):
        if self.role == "STUDENT":
            if self.house_id is None:
                raise ValueError("house_id is required for STUDENT role")
            if self.section_id is None:
                raise ValueError("section_id is required for STUDENT role")
        return self

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshRequest(BaseModel):
    refresh_token: str
