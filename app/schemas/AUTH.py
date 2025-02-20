from pydantic import BaseModel, EmailStr
from typing import Optional
from app.schemas import KUMapBaseResponse

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(KUMapBaseResponse):
    access_token: str
    refresh_token: str

class DuplicateCheckRequest(BaseModel):
    email: Optional[EmailStr] = None
    nickname: Optional[str] = None

class RegisterRequset(BaseModel):
    name: str
    nickname: str
    email: EmailStr
    password: str

class ProtectedResponse(KUMapBaseResponse):
    email: EmailStr
    name: str
    nickname: str
    phone: str
    phone_verified: bool
    image: str

class ResetPasswordRequest(BaseModel):
    email: EmailStr
