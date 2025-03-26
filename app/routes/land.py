from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import get_db
from app.config.auth import JWTBearer
from app.functions import land
from app.functions import text_generate
from app.models.user import User, UserFavoriteLand
from app.schemas import LAND, KUMapBaseResponse

# router
land_router = APIRouter(prefix="/land")


@land_router.get("/get-land-data", response_model=LAND.GetLandDataResponse)
def get_land_data(
    request: LAND.GetLandRequest = Depends(),
    payload: dict = Depends(JWTBearer(auto_error=False)),
    db: Session = Depends(get_db),
):
    like = False
    total_like = 0
    if payload:
        email = payload.get("sub")
        if email:
            user = db.query(User).filter(User.email == email).first()
            if not user:
                raise HTTPException(
                    status_code=404, detail="사용자가 존재하지 않습니다."
                )
            favorite_land = (
                db.query(UserFavoriteLand)
                .filter(
                    UserFavoriteLand.user_id == user.user_id,
                    UserFavoriteLand.pnu == request.pnu,
                )
                .first()
            )
            if favorite_land:
                like = True

    try:
        data = land.get_land_data(request.pnu, db)
        total_like = (
            db.query(UserFavoriteLand)
            .filter(UserFavoriteLand.pnu == request.pnu)
            .count()
        )
        return {
            "status": "success",
            "message": "해당 토지의 정보를 성공적으로 받아왔습니다.",
            "data": data,
            "like": like,
            "total_like": total_like,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@land_router.get(
    "/get-land-predicted-price", response_model=LAND.GetLandPredictedPriceResponse
)
def get_land_predicted_price(
    request: LAND.GetLandRequest = Depends(), db: Session = Depends(get_db)
):
    try:
        predict_price = land.set_land_predict_price_data(request.pnu, db)
        return {
            "status": "success",
            "message": "해당 토지의 예측가를 성공적으로 받아왔습니다.",
            "predict_price": predict_price,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@land_router.get("/get-land-report", response_model=KUMapBaseResponse)
def get_land_report(
    request: LAND.GetLandRequest = Depends(),
    # payload: dict = Depends(JWTBearer(auto_error=False)),
    db: Session = Depends(get_db),
):
    text_generate.generate(request.pnu, db)
    return {
        "status": "success",
        "message": "굿",
    }
