from fastapi import UploadFile, File, Form
from pydantic import BaseModel, EmailStr
from typing import Optional
from app.schemas import KUMapBaseResponse

class ResetPasswordRequest(BaseModel):
    email: EmailStr

class ChangeUserPasswordRequest(BaseModel):
    current_password: str
    change_password: str
    