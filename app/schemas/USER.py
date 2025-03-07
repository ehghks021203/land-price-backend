from fastapi import UploadFile, File, Form
from pydantic import Field, BaseModel, EmailStr
from typing import Optional
from app.schemas import KUMapBaseResponse

# requests
class ResetPasswordRequest(BaseModel):
  email: EmailStr

class ChangeUserPasswordRequest(BaseModel):
  current_password: str
  change_password: str

class ChangeLandLikeRequest(BaseModel):
  pnu: str = Field(..., description='PNU코드')

# responses
class ChangeLandLikeResponse(KUMapBaseResponse):
  like: bool = Field(..., description='해당 토지의 좋아요 여부')
  
class GetFavoriteLandsByUserResponse(KUMapBaseResponse):
  favorites: list = Field(..., description='좋아요 한 토지 목록')