from fastapi import FastAPI
from pydantic import BaseModel
#from app.routes import auth, geographical_info, get_land_data, get_land_list, land_favorites, land_info, land_list, land_management, profile, region_marker, server_status, user_land

app = FastAPI()

# 라우터 등록
#app.include_router(auth.router)
#app.include_router(geographical_info.router)
#app.include_router(get_land_data.router)
#app.include_router(get_land_list.router)
#app.include_router(land_favorites.router)
#app.include_router(land_info.router)
#app.include_router(land_list.router)
#app.include_router(land_management.router)
#app.include_router(profile.router)
#app.include_router(region_marker.router)
#app.include_router(server_status.router)
#app.include_router(user_land.router)

class ItemOut(BaseModel):
    result: str
    msg: str
    err_code: str

@app.get("/", response_model=ItemOut)
def server_status():
    return {
        "result":"success", 
        "msg":"server is online",
        "err_code":"00"
    }