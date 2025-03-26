import xgboost as xgb
import pandas as pd
import app.functions.make_input_data as mid
from app.config import model


def predict(pnu: str, year: int, month: int, return_all=False) -> int:
    loaded_model = xgb.XGBRegressor()
    loaded_model.load_model(model.MODEL_PATH)
    target_land = mid.make(pnu, f"{year:04d}{month:02d}")
    target_feature = {}
    for feature in loaded_model.feature_names_in_:
        if feature not in target_land.keys():
            if feature.split("_")[0] == "Sido":
                target_feature[feature] = (
                    feature.split("_")[1] == target_land["PNU"][0:2]
                )
            elif feature.split("_")[0] == "LandUsePlans":
                target_feature[feature] = feature.split("_")[1] in target_land[
                    "LandUsePlans"
                ].split("/")
            else:
                target_feature[feature] = (
                    feature.split("_")[1] in target_land[feature.split("_")[0]]
                )
        else:
            target_feature[feature] = target_land[feature]

    target_x = pd.DataFrame.from_dict(
        data=[target_feature], orient="columns", dtype=float
    )
    target_predict = loaded_model.predict(target_x)
    if return_all:
        return target_x, target_predict
    else:
        return abs(int(f"{target_predict[0]:.0f}")) / 1000 * 1000
