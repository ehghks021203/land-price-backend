from PyKakao import Local
from app.config.key import KAKAO_API_KEY
from app.functions.convert_code import code2addr


def get_pnu(lat: float, lng: float) -> tuple:
    try:
        local = Local(service_key=KAKAO_API_KEY)
        request_address = local.geo_coord2address(lng, lat, dataframe=False)
        request_region = local.geo_coord2regioncode(lng, lat, dataframe=False)

        if request_region == None:
            return None, None
        i = 0 if request_region["documents"][0]["region_type"] == "B" else 1
        pnu = request_region["documents"][i]["code"]
        address = request_region["documents"][i]["address_name"]

        if request_address["documents"][i]["address"]["mountain_yn"] == "N":
            mountain = "1"  # 산 X
        else:
            mountain = "2"  # 산 O

        # 본번과 부번의 포멧을 '0000'으로 맞춰줌
        main_no = request_address["documents"][0]["address"]["main_address_no"].zfill(4)
        sub_no = request_address["documents"][0]["address"]["sub_address_no"].zfill(4)
        pnu = str(pnu + mountain + main_no + sub_no)
        address = code2addr(pnu, dict_format=True)

        return pnu, address
    except Exception as e:
        print(e)
        return None, None


def get_coord(word: str) -> tuple:
    local = Local(service_key=KAKAO_API_KEY)
    address = local.search_address(word, dataframe=False)

    if len(address["documents"]) == 0:
        return None, None
    lng = float(address["documents"][0]["x"])
    lat = float(address["documents"][0]["y"])
    return lat, lng


def auto_complete_address(query: str):
    try:
        local = Local(service_key=KAKAO_API_KEY)
        response = local.search_keyword(query, dataframe=False, size=15)["documents"]
        related_search = []
        for r in response:
            related_search.append(
                {
                    "address": r["address_name"],
                    "road_address": r["road_address_name"],
                    "lat": r["y"],
                    "lng": r["x"],
                }
            )
    except:
        related_search = []
    return related_search
