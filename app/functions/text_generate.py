from datetime import datetime
from dataclasses import asdict
import google.generativeai as genai
from sqlalchemy.orm import Session
import xgboost as xgb
from app.config.model import MODEL_PATH
from app.config.key import VWORLD_API_KEY, ECOS_API_KEY, GOOGLE_API_KEY
from app.functions.api import (
    LandFeatureAPI,
    LandUsePlanAPI,
    LandTradeAPI,
    FluctuationRateOfLandPriceAPI,
    ProducerPriceIndexAPI,
    ConsumerPriceIndexAPI,
)
from app.functions.convert_code import code2addr

from app.models.land import LandInfo

PROMPT = """
너는 토지의 가치를 평가하는 전문 감정평가사야. 주어진 토지 정보를 바탕으로 일반 사용자가 쉽게 이해할 수 있는 감정평가서를 작성해줘.
토지 가격은 논리적으로 산출하고, 그 근거를 결정트리와 비교군 토지 정보를 활용해 설명해.
설명은 전문적이되, 어려운 용어나 영문 변수명은 사용하지 말고, 자연스럽고 담백한 톤으로 작성해.
모든 분석이 끝나면 제곱미터당 가격과 토지 면적을 곱한 총액을 명확히 제시해.

### 평가 대상 토지
- 주소: {target_address}
- 정보: 
    {target_info}

### 분석에 사용할 자료
1. **결정트리**:
    {tree_text}
    - 가격 산정의 논리적 근거로 활용하되, '결정트리'라는 용어는 언급하지 말고 자연스럽게 설명해.
2. **비교군 토지 정보**:
    {compare_info}
    - 주변 비슷한 토지의 최근 매매 내역을 참고해 근거를 보강하고, 비교군이 없으면 이 부분은 생략해.

### 작성 방식
1. **시작**:
    "{target_address} 토지의 가격은 {target_price}원으로 산정되었습니다. 이에 대한 근거는 다음과 같습니다."로 시작해.
2. **분석**:
    - 토지 특성 분석, 입지 분석, 비교 사례 분석을 순서대로 진행해.
    - 정보가 없는 항목은 "해당사항 없습니다."로 작성해.
3. **결론**:
    - 제곱미터당 가격을 먼

### 출력 예시
## 토지 가격 평가 설명
- 평가 토지: {}
- 면적:
- 지목:

"""

class LandInfoData():
    def __init__(self):
        self.pnu = ""
        self.land_register = ""
        self.land_classification = ""
        self.land_zoning = ""
        self.land_use_situation = ""
        self.land_height = ""
        self.land_form = ""
        self.road_side = ""
        self.land_uses = ""
        self.land_area = ""
        self.official_land_price = ""
        self.land_index = ""
        self.land_change_rt = ""
        self.land_accumulate_change_rt = ""
        self.large_cl_index = ""
        self.large_cl_change_rt = ""
        self.large_cl_accumulate_change_rt = ""
        self.ppi = ""
        self.cpi = ""
    
    def feature_parsing(self, data: dict) -> None:
        self.pnu = data["pnu"]
        self.land_register = data["regstrSeCodeNm"]
        self.land_classification = data["lndcgrCodeNm"]
        self.land_zoning = data["prposArea1Nm"]
        self.land_use_situation = data["ladUseSittnNm"]
        self.land_height = data["tpgrphHgCodeNm"]
        self.land_form = data["tpgrphFrmCodeNm"]
        self.road_side = data["roadSideCodeNm"]
        self.land_area = data["lndpclAr"]
        self.official_land_price = data["pblntfPclnd"]

    def land_use_parsing(self, data: str) -> None:
        self.land_uses = data

    def land_fluctuation_rate_parsing(self, data: dict) -> None:
        self.land_index = str(data["pclndIndex"])
        self.land_change_rt = str(data["pclndChgRt"]) + "%"
        self.land_accumulate_change_rt = str(data["acmtlPclndChgRt"]) + "%"

    def large_cl_fluctuation_rate_parsing(self, data: dict) -> None:
        print(data)
        self.large_cl_index = str(data["pclndIndex"])
        self.large_cl_change_rt = str(data["pclndChgRt"]) + "%"
        self.large_cl_accumulate_change_rt = str(data["acmtlPclndChgRt"]) + "%"

    def ppi_parsing(self, ppi: float) -> None:
        self.ppi = str(ppi)
    
    def cpi_parsing(self, cpi: float) -> None:
        self.cpi = str(cpi)

    def return_to_prompt(self) -> str:
        return f"""
        필지: {self.land_register}
        지목: {self.land_classification}
        용도지역: {self.land_zoning}
        이용상황: {self.land_use_situation}
        지세: {self.land_height}
        형상: {self.land_form}
        도로접면: {self.road_side}
        이용계획: {self.land_uses}
        면적: {self.land_area}㎡
        공시지가: {self.official_land_price}원/㎡
        지가지수: {self.land_index}
        지가변동률: {self.land_change_rt}
        누계지가변동률: {self.land_accumulate_change_rt}
        권역별지가지수: {self.large_cl_index}
        권역별지가변동률: {self.large_cl_change_rt}
        권역별누계지가변동률: {self.large_cl_accumulate_change_rt}
        생산자물가지수: {self.ppi}
        소비자물가지수: {self.cpi}
        """

def _get_land_feature_data(pnu: str, year: int, month: int):
    land_info = LandInfoData()
    # 토지 정보 및 이용계획 받아오기
    lf_api = LandFeatureAPI(key=VWORLD_API_KEY)
    land_info.feature_parsing(data=lf_api.get_data(pnu, year))
    lup_api = LandUsePlanAPI(key=VWORLD_API_KEY)
    land_info.land_use_parsing(lup_api.get_data(pnu, return2name=True))
    # 지가변동률 받아오기
    frolp_api = FluctuationRateOfLandPriceAPI(key=VWORLD_API_KEY)
    land_info.land_fluctuation_rate_parsing(data=frolp_api.get_data_by_region(pnu, year, month))
    land_info.large_cl_fluctuation_rate_parsing(data=frolp_api.get_data_by_large_region(pnu, year, month))
    # 생산자 및 소비자 물가 지수 받아오기
    ppi_api = ProducerPriceIndexAPI(key=ECOS_API_KEY)
    cpi_api = ConsumerPriceIndexAPI(key=ECOS_API_KEY)
    land_info.ppi_parsing(ppi=ppi_api.get_data(year, month))
    land_info.cpi_parsing(cpi=cpi_api.get_data(year, month))
    print(land_info.return_to_prompt())

def _get_land_trade_data(land: LandInfoData, year: int, month: int):
    # TODO: 유사 토지 거래 사례 받아오기 기능
    lt_api = LandTradeAPI(key=VWORLD_API_KEY)
    compare_land_trade = {}

    while True:
        result = lt_api.get_data(land.pnu[:5], year, month)
        if not result:
            month -= 1
            if month == 0:
                month = 12
                year -= 1
            if year == 2000:
                break
            continue
        for r in result:
            if isinstance(r, dict):
                if r["지목"] == land.land_classification:
                    print(r)
                    if r.get("용도지역"):
                        if r["용도지역"] == land.land_zoning:
                            compare_land_trade = r
                            break
    if compare_land_trade != {}:
        print(compare_land_trade)

def generate(pnu: str, db: Session):
    # 예측 모델 불러오기
    model = xgb.XGBRegressor()
    model.load_model(MODEL_PATH)
    # 제미나이 예측 모델 불러오기
    genai.configure(api_key=GOOGLE_API_KEY)
    llm_model = genai.GenerativeModel("gemini-1.5-flash")

    # 지번 주소 받아오기
    target_address = code2addr(pnu)
    # 금일 날짜 받아오기
    year = int(datetime.now().strftime("%Y"))
    month = int(datetime.now().strftime("%m"))
    # 토지 예측가 받아오기
    land_info = db.query(LandInfo).filter(LandInfo.pnu == pnu).first()
    if not land_info:
        return None
    target_price = land_info.predict_land_price
    # 토지 정보 받아오기
    target_info = _get_land_feature_data(pnu, year, month)
    # 주변 상권 정보 받아오기

    # 토지 정보 정제

    tree_text = ""
    tree_dump = model.get_booster().get_dump()
    for i, tree in enumerate(tree_dump):
        tree_text += f"Tree {i}:\n{tree}"

    # 주변의 유사 토지 거래 사례 받아오기
    compare_info = _get_land_trade_data(pnu, year, month)
    
    