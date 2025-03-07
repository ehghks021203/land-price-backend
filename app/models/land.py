from sqlalchemy import Column, Integer, String, Float, Text, TIMESTAMP
from sqlalchemy.sql import func
from app import Base

class LandInfo(Base):
  __tablename__ = 'land_info'

  pnu = Column(String(20), primary_key=True, comment='필지번호 (PNU)')
  land_feature_stdr_year = Column(Integer, nullable=False, comment='토지특성 기준년도')
  official_land_price = Column(Float, nullable=False, comment='공시지가')
  predict_land_price = Column(Float, nullable=True, comment='예측된 토지가격')
  land_classification = Column(String(10), nullable=False, comment='지목 (토지 분류)')
  land_zoning = Column(String(20), nullable=False, comment='용도지역')
  land_use_situation = Column(String(20), nullable=False, comment='토지이용 상황')
  land_register = Column(String(10), nullable=False, comment='토지 등록 구분')
  land_area = Column(Float, nullable=False, comment='토지 면적 (㎡)')
  land_height = Column(String(10), nullable=False, comment='지형 높이')
  land_form = Column(String(10), nullable=False, comment='지형 형태')
  road_side = Column(String(10), nullable=False, comment='도로 접면 여부')
  land_uses = Column(Text, nullable=True, comment='토지 이용 계획')

  generated_at = Column(TIMESTAMP, server_default=func.now(), comment='데이터 생성일시')
  predicted_at = Column(TIMESTAMP, server_default=None, comment='예측일시')

  def __repr__(self):
    return f'<LandInfo(pnu={self.pnu}, official_land_price={self.official_land_price}, land_area={self.land_area})>'
