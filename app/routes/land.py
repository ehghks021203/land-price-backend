from fastapi import APIRouter, Depends, HTTPException, Query
import json
from typing import List
from sqlalchemy.orm import Session
from app import get_db
from app.config.auth import JWTBearer
from app.config.key import VWORLD_API_KEY
from app.functions.api import GetGeometryDataAPI
from app.functions import geo
from app.functions import land
from app.models.land import LandInfo
from app.models.user import User, UserFavoriteLand
from app.schemas import LAND, KUMapBaseResponse

# router
land_router = APIRouter(prefix='/land')

@land_router.get('/get-land-data', response_model=LAND.GetLandDataResponse)
async def get_land_data(
  request: LAND.GetLandDataRequest = Depends(), 
  payload: dict = Depends(JWTBearer(auto_error=False)), 
  db: Session = Depends(get_db)
):
  like = False
  if payload:
    email = payload.get('sub')
    if email:
      user = db.query(User).filter(User.email == email).first()
      if not user:
        raise HTTPException(status_code=404, detail='사용자가 존재하지 않습니다.')
      favorite_land = (
        db.query(UserFavoriteLand)
        .filter(UserFavoriteLand.user_id == user.user_id, UserFavoriteLand.pnu == request.pnu)
        .first()
      )
      if favorite_land:
        like = True

  try:
    data = land.get_land_data(request.pnu, db)
    return {
      'status': 'success',
      'message': '해당 토지의 정보를 성공적으로 받아왔습니다.',
      'data': data,
      'like': like,
    }
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))
  