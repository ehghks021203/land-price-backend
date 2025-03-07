from datetime import datetime
import pytz
from sqlalchemy.orm import Session
from app.functions.api import LandFeatureAPI, LandTradeAPI, LandUsePlanAPI
from app.functions.convert_code import code2addr
from app.functions.geo import get_coord
from app.config.key import VWORLD_API_KEY
from app.models.land import LandInfo
from app.schemas import LAND

def _generate_land_data(pnu: str):
  address = code2addr(pnu, dict_format=True)
  lat, lng = get_coord(address['fulladdr'])
  if pnu is None or address is None:
    return None
  target_year = datetime.now(pytz.timezone("Asia/Seoul")).year

  # 토지 특성 정보 받아오기
  lf_api = LandFeatureAPI(key=VWORLD_API_KEY)
  lf_result = lf_api.get_data(pnu, target_year)
  if lf_result is None:
    return None
  
  # 토지 이용 계획 정보 받아오기
  lup_api = LandUsePlanAPI(key=VWORLD_API_KEY)
  lup_result = lup_api.get_data(pnu, return2name=True)
  if lup_result is None:
    lup_result = '없음'

  land_detail = {
    'official_price': lf_result['pblntfPclnd'],
    'predict_price': None,
    'land_cls': lf_result['lndcgrCodeNm'],
    'land_zoning': lf_result['prposArea1Nm'],
    'land_usage': lf_result['ladUseSittnNm'],
    'register': lf_result['regstrSeCodeNm'],
    'area': lf_result['lndpclAr'],
    'height': lf_result['tpgrphHgCodeNm'],
    'form': lf_result['tpgrphFrmCodeNm'],
    'road_side': lf_result['roadSideCodeNm'],
    'use_plan': lup_result,
  }
  land_detail = LAND.LandDetail(**land_detail)

  land = {
    'pnu': pnu,
    'address': address,
    'lat': lat,
    'lng': lng,
    'detail': land_detail,
    'last_predict_date': None,
    'land_feature_stdr_year': lf_result["stdrYear"],
    'land_trade_list': [],
    'auction': None,
    'listing': None,
  }

  land = LAND.Land(**land)
  return land

def get_land_data(pnu: str, db: Session):
  address = code2addr(pnu, dict_format=True)
  lat, lng = get_coord(address['fulladdr'])
  if pnu is None or address is None:
    return None

  land_info = db.query(LandInfo).filter(LandInfo.pnu == pnu).first()
    
  if land_info:
    land_detail = LAND.LandDetail(
      official_price=land_info.official_land_price,
      predict_price=land_info.predict_land_price,
      land_cls=land_info.land_classification,
      land_zoning=land_info.land_zoning,
      land_usage=land_info.land_use_situation,
      register=land_info.land_register,
      area=land_info.land_area,
      height=land_info.land_height,
      form=land_info.land_form,
      road_side=land_info.road_side,
      use_plan=land_info.land_uses,
    )

    land = LAND.Land(
      pnu=pnu,
      address=address,
      lat=lat,
      lng=lng,
      detail=land_detail,
      last_predict_date=land_info.predicted_at,
      land_feature_stdr_year=land_info.land_feature_stdr_year,
      land_trade_list=[],
      auction=None,
      listing=None,
    )
    return land

  # DB에 데이터가 없으면 API로 조회 후 저장
  new_land = _generate_land_data(pnu)
  if new_land:
    new_land_info = LandInfo(
      pnu=pnu,
      land_feature_stdr_year=new_land.land_feature_stdr_year,
      official_land_price=new_land.detail.official_price,
      predict_land_price=new_land.detail.predict_price,
      land_classification=new_land.detail.land_cls,
      land_zoning=new_land.detail.land_zoning,
      land_use_situation=new_land.detail.land_usage,
      land_register=new_land.detail.register,
      land_area=new_land.detail.area,
      land_height=new_land.detail.height,
      land_form=new_land.detail.form,
      road_side=new_land.detail.road_side,
      land_uses=new_land.detail.use_plan,
    )
    db.add(new_land_info)
    db.commit()
    db.refresh(new_land_info)
    return new_land

  return None

