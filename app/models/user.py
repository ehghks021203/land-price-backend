from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP
from sqlalchemy.sql import func
from app import Base

class User(Base):
  __tablename__ = 'user'

  user_id = Column(Integer, primary_key=True, autoincrement=True, comment='사용자 고유 ID')
  role = Column(Integer, nullable=False, default=1, comment='사용자 역할 (1: 일반 사용자, 2: 관리자 등)')
  email = Column(String(100), nullable=False, unique=True, comment='사용자 이메일')
  password = Column(String(255), nullable=False, comment='사용자 비밀번호')
  name = Column(String(20), nullable=False, comment='사용자 이름')
  nickname = Column(String(20), nullable=False, comment='사용자 닉네임')
  phone = Column(String(20), nullable=True, comment='사용자 전화번호')
  phone_verified = Column(Boolean, nullable=False, default=False, comment='전화번호 인증 여부')
  profile_image_url = Column(String(255), nullable=True, comment='프로필 이미지 URL')
  created_at = Column(TIMESTAMP, server_default=func.now(), comment='생성일시')
  modified_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now(), comment='수정일시')
  last_login = Column(TIMESTAMP, server_default=func.now(), comment='마지막 로그인 일시')

  def __repr__(self):
    return f'<User(user_id={self.user_id}, email={self.email}, name={self.name})>'
    

class UserFavoriteLand(Base):
  __tablename__ = 'user_favorite_land'

  like_id = Column(Integer, primary_key=True, autoincrement=True, comment='좋아요 ID')
  user_id = Column(Integer, nullable=False, index=True, comment='사용자 ID')
  pnu = Column(String(20), nullable=False, index=True, comment='PNU 코드')

  def __repr__(self):
    return f'<UserFavoriteLand(like_id={self.like_id}, user_id={self.user_id}, pnu={self.pnu})>'
