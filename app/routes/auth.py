from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
import random
import re
import string
import smtplib
from sqlalchemy.orm import Session
from app import get_db, SessionLocal, engine
from app.config.auth import SECRET_KEY
from app.config.mail import SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD
from app.functions.auth import create_access_token
from app.models.user import User
from app.schemas import AUTH, KUMapBaseResponse

auth_router = APIRouter(prefix='/auth')

# JWT setting
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# password hashing
password_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# OAuth2 schema
oauth2_schema = OAuth2PasswordBearer(tokenUrl='auth/login')

@auth_router.post('/login', response_model=AUTH.LoginResponse)
def login(request: AUTH.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail='아이디 또는 비밀번호가 잘못되었습니다.')
    
    if not password_context.verify(request.password, user.password):
        raise HTTPException(status_code=401, detail='아이디 또는 비밀번호가 잘못되었습니다.')
    
    # create JWT token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={'sub': user.email}, expires_delta=access_token_expires)
    refresh_token = create_access_token(data={'sub': user.email})

    return {
        'status': 'success',
        'message': '로그인에 성공하였습니다.',
        'err_code': '00',
        'access_token': access_token,
        'refresh_token': refresh_token,
    }
    
@auth_router.post('/dup-check', response_model=KUMapBaseResponse)
def duplicate_check(request: AUTH.DuplicateCheckRequest, db: Session = Depends(get_db)):
    if request.email and db.query(User).filter(User.email == request.email).first():
        raise HTTPException(status_code=409, detail='User already exists with this email')
    
    if request.nickname and db.query(User).filter(User.nickname == request.nickname).first():
        raise HTTPException(status_code=409, detail='Duplicate nickname')
    
    return {
        'status': 'success',
        'message': 'no duplicate values found',
        'err_code': '00',
    }

@auth_router.post('/register', response_model=KUMapBaseResponse)
def register(request: AUTH.RegisterRequset, db: Session = Depends(get_db)):
    # format check
    # email
    if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", user.email):
        raise HTTPException(status_code=400, detail="Invalid email format")
    # nickname
    if not re.match(r"^[ㄱ-ㅎ|가-힣|a-zA-Z0-9]{1,8}$", user.nickname):
        raise HTTPException(status_code=400, detail="Invalid nickname format or length")
    # password
    if not re.match(r"^(?=.*[a-zA-Z])(?=.*[!@#$%^*+=-])(?=.*[0-9]).{10,25}$", user.password):
        raise HTTPException(status_code=400, detail="Invalid password format or length")

    # duplicate check
    if db.query(User).filter(User.email == request.email).first():
        raise HTTPException(status_code=409, detail="User already exists with this email")

    if db.query(User).filter(User.nickname == request.nickname).first():
        raise HTTPException(status_code=409, detail="Duplicate nickname")
    
    hashed_password = password_context.hash(request.password)

    new_user = User(
        email=request.email,
        password=hashed_password,
        name=request.name,
        nickname=request.nickname,
    )
    db.add(new_user)
    db.commit()

    return {
        'status': 'success',
        'message': 'registration successful',
        'err_code': '00',
    }

@auth_router.get('/protected', response_model=AUTH.ProtectedResponse)
def protected(token: str = Depends(oauth2_schema), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get('sub')
        if not email:
            raise HTTPException(status_code=401, detail='Invalid token')

        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail='User not found')

        return {
            'status': 'success',
            'message': 'user authentication',
            'err_code': '00',
            'email': user.email,
            'user': user.nickname,
            'name': user.name,
        }
    except JWTError:
        raise HTTPException(status_code=401, detail='Invalid token')

@auth_router.post('/reset-password', response_model=KUMapBaseResponse)
def reset_password(request: AUTH.ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail='이메일이 존재하지 않습니다.')
    
    random_password = (
        ''.join(random.sample(string.ascii_letters, 8))
        + ''.join(random.sample(string.digits, 3))
        + ''.join(random.sample(string.punctuation, 1))
    )

    hashed_password = password_context.hash(random_password)
    user.password = hashed_password.decode('utf-8')
    db.commit()

    # send to email
    try:
        msg = MIMEMultipart()
        msg["From"] = SMTP_USERNAME
        msg["To"] = request.email
        msg["Subject"] = "비밀번호 초기화"
        body = f"""새로운 비밀번호는 아래와 같습니다.

        PW: {random_password}

        계정에 접속하여 비밀번호를 변경하실 것을 권장드립니다.
        감사합니다.
        """
        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SMTP_USERNAME, request.email, msg.as_string())
        server.quit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")

    return {
        'status': 'success', 
        'message': '임시 비밀번호를 메일로 전송하였습니다.',
        'err_code': '00',
    }
