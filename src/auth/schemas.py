from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    is_private: bool
    model_config = ConfigDict(extra="forbid")


class RefreshRequest(BaseModel):
    refresh_token: str
    model_config = ConfigDict(extra="forbid")


class VerifyOTP(BaseModel):
    otp: str
    model_config = ConfigDict(extra="forbid")


class ForgotPassword(BaseModel):
    email: EmailStr
    model_config = ConfigDict(extra="forbid")


class ChangePassword(BaseModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)
    model_config = ConfigDict(extra="forbid")


class DeleteAccountRequest(BaseModel):
    password: str = Field(min_length=8, max_length=128)
    model_config = ConfigDict(extra="forbid")


class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_private: bool
    last_login: datetime | None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    model_config = ConfigDict(from_attributes=True)


class ResetPassword(BaseModel):
    email: EmailStr
    otp: str = Field(min_length=6, max_length=6)
    new_password: str = Field(min_length=8, max_length=128)
    model_config = ConfigDict(extra="forbid")
