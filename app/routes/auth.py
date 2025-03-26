from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from passlib.context import CryptContext
import re
from sqlalchemy.orm import Session
from app import get_db
from app.config.auth import JWTBearer
from app.config.server import SERVER_DOMAIN
from app.functions.auth import create_access_token
from app.models.user import User
from app.schemas import AUTH, KUMapBaseResponse

auth_router = APIRouter(prefix="/auth")

# JWT setting
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 300

# password hashing
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 schema
oauth2_schema = OAuth2PasswordBearer(tokenUrl="auth/login")


@auth_router.post("/login", response_model=AUTH.LoginResponse)
async def login(request: AUTH.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(
            status_code=404, detail="아이디 또는 비밀번호가 잘못되었습니다."
        )

    if not password_context.verify(request.password, user.password):
        raise HTTPException(
            status_code=401, detail="아이디 또는 비밀번호가 잘못되었습니다."
        )

    # create JWT token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    refresh_token = create_access_token(data={"sub": user.email})

    return {
        "status": "success",
        "message": "로그인에 성공하였습니다.",
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


@auth_router.post("/dup-check", response_model=KUMapBaseResponse)
async def duplicate_check(
    request: AUTH.DuplicateCheckRequest, db: Session = Depends(get_db)
):
    if request.email and db.query(User).filter(User.email == request.email).first():
        raise HTTPException(
            status_code=409, detail="User already exists with this email"
        )

    if (
        request.nickname
        and db.query(User).filter(User.nickname == request.nickname).first()
    ):
        raise HTTPException(status_code=409, detail="Duplicate nickname")

    return {
        "status": "success",
        "message": "사용 가능합니다.",
    }


@auth_router.post("/sign-up", response_model=KUMapBaseResponse)
async def signup(request: AUTH.RegisterRequset, db: Session = Depends(get_db)):
    # format check
    # email
    if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", request.email):
        raise HTTPException(status_code=400, detail="Invalid email format")
    # nickname
    if not re.match(r"^[ㄱ-ㅎ|가-힣|a-zA-Z0-9]{1,20}$", request.nickname):
        raise HTTPException(status_code=400, detail="Invalid nickname format or length")
    # password
    if not re.match(
        r"^(?=.*[a-zA-Z])(?=.*[!@#$%^*+=-])(?=.*[0-9]).{10,25}$", request.password
    ):
        raise HTTPException(status_code=400, detail="Invalid password format or length")

    # duplicate check
    if db.query(User).filter(User.email == request.email).first():
        raise HTTPException(
            status_code=409, detail="User already exists with this email"
        )

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
        "status": "success",
        "message": "회원가입을 완료하였습니다.",
    }


@auth_router.get("/protected", response_model=AUTH.ProtectedResponse)
async def protected(
    payload: dict = Depends(JWTBearer()), db: Session = Depends(get_db)
):
    try:
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="Invalid token")

        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        return {
            "status": "success",
            "message": "사용자 인증에 성공하였습니다.",
            "email": user.email,
            "nickname": user.nickname,
            "name": user.name,
            "phone": user.phone if user.phone is not None else "",
            "phone_verified": user.phone_verified,
            "image": SERVER_DOMAIN
            + (
                user.profile_image_url
                if user.profile_image_url is not None
                else "/user/images"
            ),
        }
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@auth_router.post("/refresh-token", response_model=AUTH.RefreshTokenResponse)
async def refresh_token(
    payload: dict = Depends(JWTBearer()), db: Session = Depends(get_db)
):
    try:
        email = payload.get("sub")
        if not email:
            raise HTTPException(status_code=401, detail="유효하지 않은 토큰입니다.")

        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")

        # 새로운 액세스 토큰 생성
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        new_access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )

        return {
            "status": "success",
            "message": "새로운 액세스 토큰 발급을 성공하였습니다.",
            "access_token": new_access_token,
        }
    except JWTError:
        raise HTTPException(status_code=401, detail="로그아웃 되었습니다.")
