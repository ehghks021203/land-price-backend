import os
from fastapi import Request, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from typing import Optional

SECRET_KEY = os.getenv('SECRET_KEY')
ALGORITHM = 'HS256'
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

class JWTBearer:
  def __init__(self, auto_error: bool = True):
    self.auto_error = auto_error

  def __call__(self, request: Request):
    token = request.headers.get('Authorization')
    if not token:
      if self.auto_error:
        raise HTTPException(
          status_code=status.HTTP_401_UNAUTHORIZED,
          detail='Authorization token missing',
          headers={'WWW-Authenticate': 'Bearer'},
        )
      return None

    try:
      token = token.split(' ')[1]
      payload = self.decode_jwt(token)
      return payload
    except JWTError:
      if self.auto_error:
        raise HTTPException(
          status_code=status.HTTP_401_UNAUTHORIZED,
          detail='Invalid token',
          headers={'WWW-Authenticate': 'Bearer'},
        )
      return None

  def decode_jwt(self, token: str):
    try:
      payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
      return payload
    except JWTError:
      raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Invalid token',
        headers={'WWW-Authenticate': 'Bearer'},
      )
