import os
import csv
from typing import Dict, Union
from app.config import BASE_DIR


def code2addr(
    code: str, scale: int = 0, dict_format: bool = False
) -> Union[str, Dict[str, str]]:
    with open(os.path.join(BASE_DIR, "data/PnuCode.csv")) as data:
        csv_mapping = list(csv.DictReader(data))
    match = next((d for d in csv_mapping if d["code"].startswith(code[:10])), None)
    if not match:
        return None

    sido, sigungu, eupmyeondong, donglee = (
        match["sido"],
        match["sigungu"],
        match["eupmyeondong"],
        match["donglee"],
    )

    if len(code) == 19:
        m = "" if code[10] == "1" else "산"
        main_n, sub_n = int(code[11:15]), int(code[15:19])
        detail = f"{main_n}-{sub_n}" if sub_n != 0 else str(main_n)
        full_address = " ".join(
            filter(None, [sido, sigungu, eupmyeondong, donglee, f"{m}{detail}"])
        )
    else:
        full_address = " ".join(filter(None, [sido, sigungu, eupmyeondong]))

    if dict_format:
        return {
            "sido": sido,
            "sigungu": sigungu,
            "eupmyeondong": eupmyeondong,
            "donglee": donglee,
            "detail": f"{m}{detail}" if len(code) == 19 else None,
            "fulladdr": full_address,
        }

    if scale > 0:
        return {1: sido, 2: sigungu, 3: eupmyeondong}.get(scale, full_address)

    return full_address
