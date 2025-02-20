from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import FileResponse
from jose import JWTError, jwt
import os
from passlib.context import CryptContext
import random
import re
import secrets
import smtplib
from typing import Optional
from sqlalchemy.orm import Session
from app import get_db, SessionLocal, engine
from app.config import BASE_DIR
from app.config.auth import JWTBearer
from app.config.mail import SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD
from app.functions.auth import create_access_token
from app.models.user import User
from app.schemas import USER, KUMapBaseResponse

# router
user_router = APIRouter(prefix='/user')

# password hashing
password_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


# @user_router.post('/reset-password', response_model=KUMapBaseResponse)
# def reset_password(request: AUTH.ResetPasswordRequest, db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.email == request.email).first()
#     if not user:
#         raise HTTPException(status_code=404, detail='이메일이 존재하지 않습니다.')
    
#     random_password = (
#         ''.join(random.sample(string.ascii_letters, 8))
#         + ''.join(random.sample(string.digits, 3))
#         + ''.join(random.sample(string.punctuation, 1))
#     )

#     user.password = password_context.hash(random_password)
#     db.commit()

#     # send to email
#     try:
#         msg = MIMEMultipart()
#         msg["From"] = SMTP_USERNAME
#         msg["To"] = request.email
#         msg["Subject"] = "비밀번호 초기화"
#         body = f"""새로운 비밀번호는 아래와 같습니다.

#         PW: {random_password}

#         계정에 접속하여 비밀번호를 변경하실 것을 권장드립니다.
#         감사합니다.
#         """
#         msg.attach(MIMEText(body, "plain"))

#         server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
#         server.starttls()
#         server.login(SMTP_USERNAME, SMTP_PASSWORD)
#         server.sendmail(SMTP_USERNAME, request.email, msg.as_string())
#         server.quit()
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

#     return {
#         'status': 'success', 
#         'message': '임시 비밀번호를 메일로 전송하였습니다.',
#         'err_code': '00',
#     }


@user_router.get('/images/{file_name}')
@user_router.get('/images')
async def get_user_image(
    file_name: Optional[str] = None
):
    if not file_name:
        return FileResponse(os.path.join(BASE_DIR, 'static/images/default-user-image.png'))
    return FileResponse(os.path.join(BASE_DIR, 'static/images/', file_name))

@user_router.post('/modify-user-info')
async def modify_user_info(
    # form-data를 처리할 때에는 BaseModel 사용 불가능 (Pydantic은 Json만 처리)
    name: str = Form(...),
    nickname: str = Form(...),
    phone: str = Form(...),
    image: Optional[UploadFile] = File(None),
    payload: dict = Depends(JWTBearer()), 
    db: Session = Depends(get_db)
):
    email = payload.get('sub')
    if not email:
        raise HTTPException(status_code=401, detail='Invalid token')
        
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail='사용자가 존재하지 않습니다.')

    image_url = None
    if image:
        current_time = datetime.now().strftime('%Y%m%d%H%M%S')
        file_extension = os.path.splitext(image.filename)[1]
        saved_file_name = f'{current_time}_{secrets.token_hex(16)}{file_extension}'
        file_path = os.path.join(BASE_DIR, 'static/images/', saved_file_name)
        with open(file_path, 'wb+') as b:
            b.write(image.file.read())
        image_url = '/user/images/' + saved_file_name

    user.name = name
    user.nickname = nickname
    user.phone = phone
    user.profile_image_url = image_url
    db.commit()
    return {
        'status': 'success', 
        'message': '정보가 수정되었습니다.',
        'err_code': '00',
    }



@user_router.post('/change-password')
def change_password(
    request: USER.ChangeUserPasswordRequest, 
    payload: dict = Depends(JWTBearer()), 
    db: Session = Depends(get_db)
):
    email = payload.get('sub')
    if not email:
        raise HTTPException(status_code=401, detail='유효한 토큰이 아닙니다.')
    
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail='사용자가 존재하지 않습니다.')

    if not password_context.verify(request.current_password, user.password):
        raise HTTPException(status_code=401, detail='비밀번호가 잘못되었습니다.')

    user.password = password_context.hash(request.change_password)
    db.commit()
    return {
        'status': 'success', 
        'message': '비밀번호가 변경되었습니다.',
        'err_code': '00',
    }

# @user_router.post('set-permissions')
# def set_permissions(request):