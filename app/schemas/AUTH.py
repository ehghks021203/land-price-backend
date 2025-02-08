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
    user: str
    name: str

class ResetPasswordRequest(BaseModel):
    email: EmailStr
