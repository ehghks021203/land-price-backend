from fastapi import FastAPI
from app import app
# from app.routes import auth, geographical_info, get_land_data, get_land_list, land_favorites, land_info, land_list, land_management, profile, region_marker, server_status, user_land

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=51203)