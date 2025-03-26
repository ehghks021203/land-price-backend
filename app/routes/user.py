from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
import os
from passlib.context import CryptContext
import random
import secrets
import string
import smtplib
from typing import Optional
from sqlalchemy.orm import Session
from app import get_db
from app.config import APP_DIR
from app.config.auth import JWTBearer
from app.config.mail import SMTP_SERVER, SMTP_PORT, SMTP_USERNAME, SMTP_PASSWORD
from app.models.user import User, UserFavoriteLand
from app.functions.land import get_land_data
from app.schemas import USER, KUMapBaseResponse

# router
user_router = APIRouter(prefix="/user")

# password hashing
password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@user_router.post("/reset-password", response_model=KUMapBaseResponse)
async def reset_password(
    request: USER.ResetPasswordRequest, db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == request.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="이메일이 존재하지 않습니다.")

    random_password = (
        "".join(random.sample(string.ascii_letters, 8))
        + "".join(random.sample(string.digits, 3))
        + "".join(random.sample(string.punctuation, 1))
    )

    user.password = password_context.hash(random_password)
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
    except Exception:
        raise HTTPException(status_code=500, detail="메일 전송에 실패하였습니다.")

    return {
        "status": "success",
        "message": "임시 비밀번호를 메일로 전송하였습니다.",
    }


@user_router.get("/images/{file_name}")
@user_router.get("/images")
async def get_user_image(file_name: Optional[str] = None):
    if not file_name:
        return FileResponse(
            os.path.join(APP_DIR, "static/images/default-user-image.png")
        )
    return FileResponse(os.path.join(APP_DIR, "static/images/", file_name))


@user_router.post("/modify-user-info", response_model=KUMapBaseResponse)
async def modify_user_info(
    # form-data를 처리할 때에는 BaseModel 사용 불가능 (Pydantic은 Json만 처리)
    name: str = Form(...),
    nickname: str = Form(...),
    phone: str = Form(...),
    is_image_deleted: bool = Form(False),
    image: Optional[UploadFile] = File(None),
    payload: dict = Depends(JWTBearer()),
    db: Session = Depends(get_db),
):
    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자가 존재하지 않습니다.")

    if is_image_deleted:
        user.profile_image_url = None
    elif image:
        current_time = datetime.now().strftime("%Y%m%d%H%M%S")
        file_extension = os.path.splitext(image.filename)[1]
        saved_file_name = f"{current_time}_{secrets.token_hex(16)}{file_extension}"
        file_path = os.path.join(APP_DIR, "static/images/", saved_file_name)
        with open(file_path, "wb+") as b:
            b.write(image.file.read())
        user.profile_image_url = "/user/images/" + saved_file_name
    user.name = name
    user.nickname = nickname
    user.phone = phone
    db.commit()

    return {
        "status": "success",
        "message": "정보가 수정되었습니다.",
    }


@user_router.post("/change-password", response_model=KUMapBaseResponse)
async def change_password(
    request: USER.ChangeUserPasswordRequest,
    payload: dict = Depends(JWTBearer()),
    db: Session = Depends(get_db),
):
    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="유효한 토큰이 아닙니다.")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자가 존재하지 않습니다.")

    if not password_context.verify(request.current_password, user.password):
        raise HTTPException(status_code=401, detail="비밀번호가 잘못되었습니다.")

    user.password = password_context.hash(request.change_password)
    db.commit()
    return {
        "status": "success",
        "message": "비밀번호가 변경되었습니다.",
    }


# @user_router.post('/set-permissions')
# def set_permissions(request):


@user_router.post("/change-land-like", response_model=USER.ChangeLandLikeResponse)
def patch_land_like_status(
    request: USER.ChangeLandLikeRequest,
    payload: dict = Depends(JWTBearer()),
    db: Session = Depends(get_db),
):
    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="유효한 토큰이 아닙니다.")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자가 존재하지 않습니다.")

    favorite_land = (
        db.query(UserFavoriteLand)
        .filter(
            UserFavoriteLand.user_id == user.user_id,
            UserFavoriteLand.pnu == request.pnu,
        )
        .first()
    )

    if favorite_land:
        # 이미 존재하면 삭제 (좋아요 취소)
        db.delete(favorite_land)
        db.commit()
        return {
            "status": "success",
            "message": "좋아요를 취소했습니다.",
            "like": False,
        }
    else:
        # 존재하지 않으면 추가 (좋아요 등록)
        new_favorite = UserFavoriteLand(user_id=user.user_id, pnu=request.pnu)
        db.add(new_favorite)
        db.commit()
        return {
            "status": "success",
            "message": "좋아요를 눌렀습니다.",
            "like": True,
        }


@user_router.get(
    "/get-favorite-lands-by-user", response_model=USER.GetFavoriteLandsByUserResponse
)
def get_favorite_land(
    payload: dict = Depends(JWTBearer()), db: Session = Depends(get_db)
):
    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="유효한 토큰이 아닙니다.")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자가 존재하지 않습니다.")

    favorite_lands_by_db = (
        db.query(UserFavoriteLand)
        .filter(UserFavoriteLand.user_id == user.user_id)
        .all()
    )

    favorite_lands = []
    for fav in favorite_lands_by_db:
        favorite_lands.append(get_land_data(pnu=fav.pnu, db=db))

    return {
        "status": "success",
        "message": "좋아요 한 토지 목록을 받아왔습니다.",
        "favorites": favorite_lands,
    }
